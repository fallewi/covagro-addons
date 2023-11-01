# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductMRPArea(models.Model):
    _inherit = "product.mrp.area"

    group_estimate_days = fields.Integer(
        string="Group Days of Estimates",
        default=1,
        help="Les jours pour regrouper vos devis en demande pour le MRP."
        "Cela peut être différent de la longueur des plages de dates que vous "
        "utilisez dans les estimations mais il ne devrait pas être supérieur, dans ce cas"
        "Seul le regroupement jusqu'à la longueur totale de la plage de dates sera effectué.",
    )

    _sql_constraints = [
        (
            "group_estimate_days_check",
            "CHECK( group_estimate_days >= 0 )",
            "Les jours de groupe d'estimations doivent être supérieurs ou égaux à zéro.",
        ),
    ]
