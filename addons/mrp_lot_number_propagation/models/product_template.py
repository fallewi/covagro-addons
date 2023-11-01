# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("tracking")
    def _check_bom_propagate_lot_number(self):
        """Block tracking type updates if the product is used by a BoM."""
        for product in self:
            if product.tracking == "serial":
                continue
            # Check BoMs
            for bom in product.bom_ids:
                if bom.lot_number_propagation:
                    raise ValidationError(
                        _(
                            "Une nomenclature propageant des numéros de série nécessite "
                            "ce produit doit être suivi en tant que tel."
                        )
                    )
            # Check lines of BoMs
            bom_lines = self.env["mrp.bom.line"].search(
                [
                    ("product_id", "in", product.product_variant_ids.ids),
                    ("propagate_lot_number", "=", True),
                    ("bom_id.lot_number_propagation", "=", True),
                ]
            )
            if bom_lines:
                boms = "\n- ".join(bom_lines.mapped("bom_id.display_name"))
                boms = "\n- " + boms
                raise ValidationError(
                    _(
                        "Ce composant est configuré pour propager ses "
                        "numéro de série dans la nomenclature suivante :{boms}'"
                    ).format(boms=boms)
                )
