# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Etiquettes MRP ",
    "summary": "Permet d'ajouter plusieurs balises aux ordres de fabrication",
    "version": "15.0.1.0.0",
    "author": "Fall Lewis" ,
    "category": "Purchases",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
        "views/mrp_tag_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
