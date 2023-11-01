# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_partial_kit_delivery = fields.Boolean(
        default=True,
        help="S'il n'est pas défini, et que ce produit est livré avec une nomenclature de type "
        "kit, les livraisons partielles des composants ne seront pas autorisées.",
    )
