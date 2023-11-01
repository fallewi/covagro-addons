# Copyright 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Demand Estimate",
    "summary": "Allows to create demand estimates.",
    "version": "15.0.1.1.0",
    "author": "Fall Lewis",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_security.xml",
        "views/stock_demand_estimate_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
