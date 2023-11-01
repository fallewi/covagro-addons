# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    stock_move_id = fields.Many2one(
        comodel_name="stock.move", string="Mouvement de Stock", copy=False, index=True
    )
    need_vehicle = fields.Boolean(string="Besoin d'un véhicule")
