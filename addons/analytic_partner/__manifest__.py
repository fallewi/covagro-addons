# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# Copyright 2018 Tecnativa - Cristina Martin R.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "COVAGRO Link analytic items and partner",
    "summary": "Search and group analytic entries by partner",
    "version": "15.0.1.0.0",
    "category": "Analytic Accounting",
    "author": "Fall lewis YOMBA (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account"],
    "data": ["views/account_analytic_line_views.xml", "views/res_partner_views.xml"],
}
