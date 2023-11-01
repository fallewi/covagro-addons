# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "COVAGRO Stock Analytic",
    "summary": "Adds an analytic account and analytic tags in stock move",
    "version": "15.0.1.1.0",
    "author": "Fall lewis YOMBA (OCA)",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": ["stock_account", "analytic"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_scrap.xml",
        "views/stock_move_line.xml",
    ],
    "installable": True,
}
