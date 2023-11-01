# Copyright 2015 ForgeFlow - Jordi Ballester Alomar
# Copyright 2015 Pedro M. Baeza - Antiun Ingeniería
# Copyright 2021 Daniel Reis - Open Source Integrators
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "COVAGRO Analytic for manufacturing",
    "summary": "Adds the analytic account to the production order",
    "version": "15.0.1.0.0",
    "category": "Manufacturing",
    "author": "Fall lewis YOMBA (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "analytic", "stock_account"],
    "data": ["views/mrp_view.xml", "views/analytic_account_view.xml"],
    "installable": True,
}
