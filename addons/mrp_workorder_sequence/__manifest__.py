# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Séquence d'ordre de travail MRP",
    "summary": "ajoute une séquence aux ordres de travail de production.",
    "version": "15.0.1.2.0",
    "category": "Manufacturing",
    "author": "Fall Lewis" ,
    "license": "LGPL-3",
    "depends": ["mrp"],
    "data": ["views/mrp_workorder_view.xml"],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
