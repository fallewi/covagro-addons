# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo https://www.escodoo.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FleetVehicleInspection(models.Model):

    _name = "fleet.vehicle.inspection"
    _description = "Fleet Vehicle Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    READONLY_STATES = {
        "confirmed": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    name = fields.Char(
        "Reference", required=True, index=True, copy=False, default="New"
    )

    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Annulé")],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
        help="* Brouillon : pas encore confirmé.\n"
        " * Confirmé : l'inspection a été confirmée.\n"
        " * Annulé : a été annulé, ne peut plus être confirmé.",
    )

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        "Vehicle",
        help="Véhicule de la flotte",
        required=True,
        states=READONLY_STATES,
    )

    odometer_id = fields.Many2one(
        "fleet.vehicle.odometer",
        "Odometer ID",
        help="Mesure de l'odomètre du véhicule au moment de ce journal",
    )

    odometer = fields.Float(
        compute="_compute_odometer",
        inverse="_inverse_odometer",
        help="Mesure de l'odomètre du véhicule au moment de ce journal",
        store=True,
        states=READONLY_STATES,
    )

    odometer_unit = fields.Selection(
        [("kilometers", "Kilometres"), ("miles", "Miles")],
        default="kilometers",
        required=True,
        states=READONLY_STATES,
    )

    date_inspected = fields.Datetime(
        "Date d'inspection",
        required=True,
        default=fields.Datetime.now,
        help="Date à laquelle le véhicule a été inspecté",
        copy=False,
        states=READONLY_STATES,
    )

    inspected_by = fields.Many2one(
        "res.partner",
        tracking=True,
        states=READONLY_STATES,
    )

    direction = fields.Selection(
        selection=[("in", "Entrée"), ("out", "Sortie")],
        default="out",
        states=READONLY_STATES,
    )

    note = fields.Html("Notes", states=READONLY_STATES)

    inspection_line_ids = fields.One2many(
        "fleet.vehicle.inspection.line",
        "inspection_id",
        copy=True,
        auto_join=True,
        states=READONLY_STATES,
    )

    result = fields.Selection(
        [("todo", "A Faire"), ("success", "Succès"), ("failure", "Échec")],
        "Inspection Result",
        default="todo",
        compute="_compute_inspection_result",
        readonly=True,
        copy=False,
        store=True,
    )

    @api.depends("inspection_line_ids", "state")
    def _compute_inspection_result(self):
        for rec in self:
            if rec.inspection_line_ids:
                if any(line.result == "todo" for line in rec.inspection_line_ids):
                    rec.result = "todo"
                elif any(line.result == "failure" for line in rec.inspection_line_ids):
                    rec.result = "failure"
                else:
                    rec.result = "success"
            else:
                rec.result = "todo"

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            if vals.get("direction") == "out":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fleet.vehicle.inspection.out")
                    or "/"
                )
            else:
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fleet.vehicle.inspection.in")
                    or "/"
                )
        return super(FleetVehicleInspection, self).create(vals)

    def button_cancel(self):
        records = self.filtered(lambda rec: rec.state in ["draft", "confirmed"])
        return records.write({"state": "cancel"})

    def button_confirm(self):
        if any(not rec.inspection_line_ids for rec in self) or any(
            line.result == "todo" for line in self.mapped("inspection_line_ids")
        ):
            raise UserError(
                _("L'inspection ne peut pas être terminée." "Il y a des éléments non inspectés.")
            )
        if any(rec.state not in ["draft", "cancel"] for rec in self):
            raise ValidationError(
                _("Seules les inspections dans les états 'brouillon' ou 'annulation' peuvent être confirmées")
            )
        return self.write({"state": "confirmed"})

    def button_draft(self):
        return self.write({"state": "draft", "result": "todo"})

    def _compute_odometer(self):
        self.odometer = 0.0
        for rec in self:
            rec.odometer = False
            if rec.odometer_id:
                rec.odometer = rec.odometer_id.value

    def _inverse_odometer(self):
        for rec in self:
            if not rec.odometer:
                raise UserError(
                    _("La vidange de la valeur de l'odomètre d'un " "véhicule n'est pas autorisée.")
                )
            odometer = self.env["fleet.vehicle.odometer"].create(
                {
                    "value": rec.odometer,
                    "date": rec.date_inspected or fields.Date.context_today(rec),
                    "vehicle_id": rec.vehicle_id.id,
                }
            )
            self.odometer_id = odometer
