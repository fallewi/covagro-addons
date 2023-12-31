# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Lot On Hand First",
    "summary": "Allows to display lots on hand first in M2o fields",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Inventory",
    "author": "Fall Lewis",
    "maintainers": ["grindtildeath"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_lot_product_qty_search", "base_view_inheritance_extension"],
    "data": [
        "views/stock_move_line.xml",
        "views/stock_move.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
    ],
}
