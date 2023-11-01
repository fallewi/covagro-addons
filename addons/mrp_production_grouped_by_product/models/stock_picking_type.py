# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    mo_grouping_max_hour = fields.Integer(
        string="Groupement MO max. heure (UTC)",
        help="L'heure maximum (entre 0 et 23) pour envisager de nouveaux "
        "commandes de fabrication à l'intérieur de la même période d'intervalle, et donc"
        " étant regroupés sur le même MO. IMPORTANT : L'heure doit être "
        "exprimé en UTC.",
        default=19,
    )
    mo_grouping_interval = fields.Integer(
        string="Intervalle de regroupement MO (jours)",
        help="Le nombre de jours pour se regrouper sur le même "
        "ordre de fabrication.",
        default=1,
    )

    @api.constrains("mo_grouping_max_hour")
    def _check_mo_grouping_max_hour(self):
        if self.mo_grouping_max_hour < 0 or self.mo_grouping_max_hour > 23:
            raise exceptions.ValidationError(
                _("Vous devez entrer une heure valide entre 0 et 23.")
            )

    @api.constrains("mo_grouping_interval")
    def _check_mo_grouping_interval(self):
        if self.mo_grouping_interval < 0:
            raise exceptions.ValidationError(
                _("Vous devez entrer une valeur positive pour l'intervalle.")
            )
