# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Répartition de la production MRP",
    "summary": "Diviser les ordres de fabrication en plus petits",
    "version": "15.0.1.0.0",
    "author": "Fall Lewis" ,
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "templates/messages.xml",
        "views/mrp_production.xml",
        "wizards/mrp_production_split_wizard.xml",
    ],
}
