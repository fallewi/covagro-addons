# Copyright 2019 Kitti U. - Ecosoft <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Aide au kit de produits pour la sélection des stocks",
    "summary": "Définir la quantité dans la ligne de prélèvement en fonction de la quantité de kit de produits",
    "version": "15.0.0.1.0",
    "category": "Stock",
    "author": "Fall Lewis" ,
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_mrp"],
    "data": ["security/ir.model.access.csv", "views/stock_view.xml"],
    "maintainers": ["kittiu"],
}
