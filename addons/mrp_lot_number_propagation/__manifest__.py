# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Propagation du numéro de série MRP",
    "version": "15.0.0.3.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Fall Lewis" ,
    "summary": "Propager un numéro de série d'un composant à un produit fini",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
    ],
    "installable": True,
    "application": False,
}
