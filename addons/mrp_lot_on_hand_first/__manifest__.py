# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Mrp Lot On Hand First",
    "summary": "Allows to display lots on hand first in M2o fields",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Manufacturing/Manufacturing",
    "author": "Fall Lewis",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "mrp",
        "stock_lot_on_hand_first",
    ],
    "data": [
        "views/mrp_production.xml",
        "views/stock_picking_type.xml",
    ],
}
