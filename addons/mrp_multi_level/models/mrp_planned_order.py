# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import timedelta

from odoo import api, fields, models


class MrpPlannedOrder(models.Model):
    _name = "mrp.planned.order"
    _description = "Ordre planifié"
    _order = "due_date, id"

    name = fields.Char(string="Description")
    origin = fields.Char(string="Documents sources")
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
        string="Zone de Fabrication",
        store=True,
        index=True,
        readonly=True,
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
        readonly=True,
    )
    order_release_date = fields.Date(
        string="Date de sortie", help="Date de lancement de la commande prévue par le MRP.", required=True
    )
    due_date = fields.Date(
        help="Date à laquelle la fourniture doit avoir été effectuée.",
        required=True,
    )
    qty_released = fields.Float(readonly=True)
    fixed = fields.Boolean(default=True)
    mrp_qty = fields.Float(string="Quantity")
    mrp_move_down_ids = fields.Many2many(
        comodel_name="mrp.move",
        relation="mrp_move_planned_order_rel",
        column1="order_id",
        column2="move_down_id",
        string="Déplacement de fabrication vers le BAS",
    )
    mrp_action = fields.Selection(
        selection=[
            ("manufacture", "Ordre de fabrication"),
            ("buy", "Bon de commande"),
            ("pull", "Stratégie pull"),
            ("push", "Stratégie push"),
            ("pull_push", "Stratégie push et pull"),
            ("none", "Aucun(e)"),
        ],
        string="Action",
    )
    mrp_inventory_id = fields.Many2one(
        string="Inventaire de fabrication associé",
        comodel_name="mrp.inventory",
        ondelete="set null",
    )
    mrp_production_ids = fields.One2many(
        "mrp.production", "planned_order_id", string="Ordres de fabrication"
    )
    mo_count = fields.Integer(compute="_compute_mrp_production_count")
    mrp_planner_id = fields.Many2one(
        related="product_mrp_area_id.mrp_planner_id",
        readonly=True,
        store=True,
    )

    def _compute_mrp_production_count(self):
        for rec in self:
            rec.mo_count = len(rec.mrp_production_ids)

    @api.onchange("due_date")
    def _onchange_due_date(self):
        if self.due_date:
            if self.product_mrp_area_id.mrp_lead_time:
                calendar = self.mrp_area_id.calendar_id
                if calendar:
                    dt = fields.Datetime.from_string(self.due_date)
                    res = calendar.plan_days(
                        -1 * (self.product_mrp_area_id.mrp_lead_time + 1), dt
                    )
                    self.order_release_date = res.date()
                else:
                    self.order_release_date = fields.Date.from_string(
                        self.due_date
                    ) - timedelta(days=self.product_mrp_area_id.mrp_lead_time)

    def action_toggle_fixed(self):
        for rec in self:
            rec.fixed = not rec.fixed

    def action_open_linked_mrp_production(self):
        action = self.env.ref("mrp.mrp_production_action")
        result = action.read()[0]
        result["context"] = {}
        result["domain"] = "[('id','in',%s)]" % self.mrp_production_ids.ids
        return result
