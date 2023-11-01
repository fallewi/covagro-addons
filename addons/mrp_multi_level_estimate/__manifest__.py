# Copyright 2019-23 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Estimation multiniveau MRP",
    "version": "15.0.1.1.0",
    "license": "LGPL-3",
    "author": "Fall Lewis" ,
    "summary": "Permet de considérer les estimations de la demande à l'aide de MRP multi-niveaux.",
    "category": "Manufacturing",
    "depends": ["mrp_multi_level", "stock_demand_estimate"],
    "data": ["views/product_mrp_area_views.xml", "views/mrp_area_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
