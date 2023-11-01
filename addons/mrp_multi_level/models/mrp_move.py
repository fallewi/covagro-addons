# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpMove(models.Model):
    _name = "mrp.move"
    _description = "Mouvement Move"
    _order = "product_mrp_area_id, mrp_date, mrp_type desc, id"

    # TODO: too many indexes...

    product_mrp_area_id = fields.Many2one(
        comodel_name="product.mrp.area",
        string="Zone de fabrication produit",
        index=True,
        required=True,
        ondelete="cascade",
    )
    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        related="product_mrp_area_id.mrp_area_id",
        string="Zone de fabrication",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="product_mrp_area_id.mrp_area_id.warehouse_id.company_id",
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="product_mrp_area_id.product_id",
        store=True,
    )

    current_date = fields.Date()
    current_qty = fields.Float()
    mrp_date = fields.Date(string="Date de Fabrication")
    planned_order_up_ids = fields.Many2many(
        comodel_name="mrp.planned.order",
        relation="mrp_move_planned_order_rel",
        column1="move_down_id",
        column2="order_id",
        string="Ordres planifiés",
    )
    mrp_order_number = fields.Char(string="Order Number")
    mrp_origin = fields.Selection(
        selection=[
            ("mo", "Ordre de fabrication"),
            ("po", "Bon de commande"),
            ("mv", "Mouvement"),
            ("fc", "Prévision"),
            ("mrp", "Fabrication"),
        ],
        string="Origine",
    )
    mrp_qty = fields.Float(string="Quantité de fabrication")
    mrp_type = fields.Selection(
        selection=[("s", "Qté Fournie"), ("d", "Qté Demande")], string="Type"
    )
    name = fields.Char(string="Description")
    origin = fields.Char(string="Documents sources")
    parent_product_id = fields.Many2one(
        comodel_name="product.product", string="Produit parent", index=True
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production", string="Ordre de fabrication", index=True
    )
    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line", string="Ligne de bon de commande", index=True
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order", string="Bon de commande", index=True
    )
    state = fields.Selection(
        selection=[
            ("draft", "Brouillon"),
            ("assigned", "Assigné"),
            ("confirmed", "Confirmé"),
            ("waiting", "En Attente"),
            ("partially_available", "Partiellement disponible"),
            ("ready", "Prêt"),
            ("sent", "Envoyé"),
            ("to approve", "A Approuver"),
            ("approved", "Approuvé"),
        ],
    )
    stock_move_id = fields.Many2one(
        comodel_name="stock.move", string="Mouvement de Stock", index=True
    )
