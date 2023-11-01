# See LICENSE file for full copyright and licensing details.
"""Model for the track operation."""

from odoo import _, fields, models
from odoo.exceptions import UserError


class WizTrackOperation(models.TransientModel):
    """Transient Model for track Record."""

    _name = "wiz.track.operation"
    _description = "Opération de piste"

    order_number = fields.Char(string="Numéro de commande")
    source_location = fields.Char(string="Emplacement de la source")
    dest_location = fields.Char(string="Emplacement de destination")
    transport = fields.Char(string="Transport")
    status = fields.Char(string="Statut")
    tracking_ids = fields.Many2many(
        "operation.tracking",
        "tracking_track_operation_rel",
        "tracking_id",
        "track_id",
        string="Suivie",
    )

    def action_track(self):
        """Track the order via order Number."""
        self.ensure_one()
        for operation in self:
            order = self.env["freight.operation"].search(
                [("name", "=", operation.order_number)], limit=1
            )
            group = self.env.user.has_group("scs_freight.freight_operation_admin")
            di = {}
            state_field = order.fields_get(["state"])
            for key, value in state_field.get("state", {}).get("selection", []):
                di.setdefault(key, value)
            if not order:
                raise UserError(
                    _("La commande d'expédition n'est pas disponible avec" " Ce [ %s ] numéro.!!")
                    % operation.order_number
                )
            if not group:
                if order.state in ["draft", "confirm"]:
                    raise UserError(_("Toujours aucune activité pour cette commande !!"))
                elif order.state == "cancel":
                    raise UserError(_("Cette commande a été annulée. !!"))
            tracks = order.mapped("tracking_ids")
            track_list = []
            for track in tracks:
                track_list.append(
                    (
                        0,
                        0,
                        {
                            "source_location_id": track.source_location_id.id or False,
                            "dest_location_id": track.dest_location_id.id or False,
                            "date": track.date or False,
                            "activity": track.activity or "",
                        },
                    )
                )
            operation.write(
                {
                    "transport": order.transport and order.transport.title() or "",
                    "status": di.get(order.state) and di.get(order.state).title() or "",
                    "source_location": order.loading_port_id
                    and order.loading_port_id.name
                    or "",
                    "dest_location": order.discharg_port_id
                    and order.discharg_port_id.name
                    or "",
                    "tracking_ids": track_list,
                }
            )
            return {
                "view_mode": "form",
                "name": "Suivre la commande d'expédition",
                "res_model": "wiz.track.operation",
                "type": "ir.actions.act_window",
                "target": "new",
                "res_id": operation.id,
            }
