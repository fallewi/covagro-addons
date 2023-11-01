# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_quantity = fields.Float(string='Minimum Quantity')
    qty_min = fields.Float(string='Minimum Quantity',compute='_compute_reorder_qty_min')

    def _compute_reorder_qty_min(self):
        for product in self:
            if product.orderpoint_ids:
                for i in product.orderpoint_ids[0]:
                    qty = i.product_min_qty
                    product.qty_min = qty
            else:
                product.qty_min = 0.0

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    temp_min_quantity = fields.Float(string='Minimum Quantity')
    temp_qty_min = fields.Float(string='Minimum Quantity',compute='_compute_reorder_qty_min')

    def _compute_reorder_qty_min(self):
        for product in self:
            if product.product_variant_id.orderpoint_ids:
                for i in product.product_variant_id.orderpoint_ids[0]:
                    qty = i.product_min_qty
                    product.temp_qty_min = qty
            else:
                product.temp_qty_min = 0.0
