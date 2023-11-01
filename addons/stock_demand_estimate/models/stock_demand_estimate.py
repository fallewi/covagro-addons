# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockDemandEstimate(models.Model):
    _name = "stock.demand.estimate"
    _description = "Ligne d'estimation de la demande de stock"

    date_from = fields.Date(
        compute="_compute_dates", string="De (calculé)", store=True
    )
    date_to = fields.Date(compute="_compute_dates", string="A (calculé)", store=True)
    manual_date_from = fields.Date(string="De")
    manual_date_to = fields.Date(string="A")
    manual_duration = fields.Integer(
        string="Duration", help="Durée (en jours)", default=1
    )
    duration = fields.Integer(
        compute="_compute_dates", string="Durée (calculée)", store=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Produit", required=True
    )
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unité de mesure")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Emplacement", required=True
    )
    product_uom_qty = fields.Float(string="Quantity", digits="Unité de mesure du produit")
    product_qty = fields.Float(
        string="Quantité (unité de quantité de produit)",
        compute="_compute_product_quantity",
        inverse="_inverse_product_quantity",
        digits=0,
        store=True,
        help="Quantité dans l'unité de quantité par défaut du produit",
        readonly=True,
    )
    daily_qty = fields.Float(string="Quantité / Jour", compute="_compute_daily_qty")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.depends("manual_duration", "manual_date_from", "manual_date_to")
    def _compute_dates(self):
        today = date.today()
        for rec in self:
            rec.date_from = rec.manual_date_from or today
            if rec.manual_date_to:
                rec.date_to = rec.manual_date_to
                rec.duration = (rec.manual_date_to - rec.date_from).days + 1
            elif rec.manual_duration:
                rec.date_to = rec.date_from + timedelta(days=rec.manual_duration - 1)
                rec.duration = rec.manual_duration
            else:
                rec.date_to = rec.date_from + timedelta(days=1)
                rec.duration = 2

    @api.depends("product_qty", "duration")
    def _compute_daily_qty(self):
        for rec in self:
            if rec.duration:
                rec.daily_qty = rec.product_qty / rec.duration
            else:
                rec.daily_qty = 0.0

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_product_quantity(self):
        for rec in self:
            if rec.product_uom:
                rec.product_qty = rec.product_uom._compute_quantity(
                    rec.product_uom_qty, rec.product_id.uom_id
                )
            else:
                rec.product_qty = rec.product_uom_qty

    def _inverse_product_quantity(self):
        raise UserError(
            _(
                "L'opération demandée ne peut pas être"
                "traité en raison d'une erreur de programmation"
                "définir le champ `product_qty` à la place "
                "de `product_uom_qty`."
            )
        )

    def name_get(self):
        res = []
        for rec in self:
            name = "{} - {}: {} - {}".format(
                rec.date_from, rec.date_to, rec.product_id.name, rec.location_id.name
            )
            res.append((rec.id, name))
        return res

    @api.onchange("manual_date_to")
    def _onchange_manual_date_to(self):
        for rec in self:
            if rec.manual_date_from:
                rec.manual_duration = (
                    rec.manual_date_to - rec.manual_date_from
                ).days + 1

    @api.onchange("manual_duration")
    def _onchange_manual_duration(self):
        for rec in self:
            if rec.manual_date_from:
                rec.manual_date_to = rec.manual_date_from + timedelta(
                    days=rec.manual_duration - 1
                )

    @api.model
    def get_quantity_by_date_range(self, date_start, date_end):
        """To be used in other modules"""
        # Check if the dates overlap with the period
        period_date_start = self.date_from
        period_date_end = self.date_to

        # We need only the periods that overlap
        # the dates introduced by the user.
        if period_date_start <= date_end and period_date_end >= date_start:
            overlap_date_start = max(period_date_start, date_start)
            overlap_date_end = min(period_date_end, date_end)
            days = (abs(overlap_date_end - overlap_date_start)).days + 1
            return days * self.daily_qty
        return 0.0
