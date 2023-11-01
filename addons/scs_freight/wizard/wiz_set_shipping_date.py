# See LICENSE file for full copyright and licensing details.
"""Transient Model for Set Received date on once click."""

from odoo import _, fields, models
from odoo.exceptions import UserError


class WizSetShippingDate(models.TransientModel):
    """Wizard Transient model."""

    _name = "wiz.set.shipping.date"
    _description = "L'assistant définit la date de réception"

    date = fields.Date(string="Date")
    ship_type = fields.Selection(
        [("recived", "Reçu"), ("delivered", "Livré")],
        string="Type d'expédition",
        default="recived",
    )
    operation_ids = fields.Many2many(
        "freight.operation",
        "freight_wizrec_rel",
        "operation_id",
        "wiz_id",
        string="Opérations d'expédition",
    )

    def action_set_date(self):
        """Set Date on shipping Operation."""
        self.ensure_one()
        for operation in self.operation_ids:
            if self.ship_type == "recived":
                if operation.direction == "import":
                    operation.write(
                        {"act_rec_date": self.date or False, "state": "recived"}
                    )
                else:
                    raise UserError(
                        _("Envoi de la commande %s est une exportation, vous ne pouvez pas définir la date de réception.")
                        % operation.name
                    )
            elif self.ship_type == "delivered":
                if operation.direction == "export":
                    operation.write(
                        {"act_send_date": self.date or False, "state": "delivered"}
                    )
                else:
                    raise UserError(
                        _(
                            "l'Envoi de la commande %s est l'importation que vous ne pouvez pas "
                            "définir la date de livraison."
                        )
                        % operation.name
                    )
            containers = operation.operation_line_ids.mapped("container_id")
            if containers:
                containers.write({"state": "available"})
