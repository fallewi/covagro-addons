# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "COVAGRO Analytic Accounts Dimensions",
    "summary": "Group Analytic Entries by Dimensions",
    "version": "15.0.1.0.1",
    "development_status": "Mature",
    "license": "AGPL-3",
    "author": "Fall lewis YOMBA (OCA)",
    "depends": ["account", "analytic"],
    "data": ["security/ir.model.access.csv", "views/analytic_view.xml"],
    "uninstall_hook": "uninstall_hook",
}
