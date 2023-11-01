# Copyright 2022 ForgeFlow S.L. (http://www.forgeflow.com)
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

	
class MRPArea(models.Model):
    _inherit = "mrp.area"

    estimate_demand_and_other_sources_strat = fields.Selection(
        string="Estimations de la demande et stratégie des autres sources de demande",
        selection=[
            ("all", "Considérez toujours toutes les sources"),
            (
                "ignore_others_if_estimates",
                "Ignorer les autres sources de produits avec des estimations",
            ),
            (
                "ignore_overlapping",
                "Ignorer les autres sources pendant les périodes avec des estimations",
            ),
        ],
        default="all",
        help="Définir la stratégie à suivre en MRP multi niveau lorsqu'il y a une"
        "coexistence de la demande à partir des estimations de la demande et d'autres sources.\n"
        "* Toujours prendre en compte toutes les sources : rien n'est exclu ou ignoré.\n"
        "* Ignorer les autres sources pour les produits avec des estimations : lorsqu'elles "
        "sont des estimations saisies pour le produit et elles sont dans un cadeau ou "
        "période future, toutes les autres sources de demande sont ignorées pour ceux "
        "produits.\n"
        "* Ignorer les autres sources pendant les périodes avec des estimations : Quand "
        "vous créez des estimations de la demande pour une période et un produit",
        "d'autres sources de demande seront ignorées pendant cette période"
        "pour ces produits.",
    )