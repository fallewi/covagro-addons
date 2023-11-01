# See LICENSE file for full copyright and licensing details.
"""This file contain operation related to service."""

from odoo import fields, models


class Product(models.Model):
    """Inherit Product Model."""

    _inherit = "product.product"

    vendor_id = fields.Many2one(
        "res.partner", string="Fournisseur", domain="[('is_vendor', '=', True)]"
    )
