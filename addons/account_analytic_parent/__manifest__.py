
{
    "name": "COVAGRO Account Analytic Parent",
    "summary": """
        This module reintroduces the hierarchy to the analytic accounts.""",
    "version": "15.0.1.0.0",
    "category": "Accounting & Finance",
    "license": "AGPL-3",
    "author": "Fall lewis YOMBA (OCA)",
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "analytic"],
    "data": ["views/account_analytic_account_view.xml"],
    "post_init_hook": "post_init_hook",
}
