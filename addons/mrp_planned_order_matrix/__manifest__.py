# Copyright 2019-22 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Matrice des commandes planifiées MRP",
    "summary": "Permet de créer des ordres planifiés fixes sur une vue de grille.",
    "version": "15.0.1.1.0",
    "author": "Fall Lewis" ,
    "category": "Warehouse Management",
    "depends": ["mrp_multi_level", "web_widget_x2many_2d_matrix", "date_range"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_planned_order_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
