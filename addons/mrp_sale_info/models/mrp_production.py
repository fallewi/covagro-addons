# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Bon de commande de Vente",
        readonly=True,
        store=True,
        related="source_procurement_group_id.sale_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Client",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date", string="Date d'engagement", store=True
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Référence client", store=True
    )
