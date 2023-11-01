# -*- coding: utf-8 -*-

{
    'name': 'Système de paie générique COVAGRO',
    'category': 'Generic Modules/Human Resources',
    'summary': """
          Système de paie générique COVAGRO intégré à la comptabilité, encodage des dépenses, encodage des paiements, gestion des contributions de l'entreprise
    """,
    'description': """Odoo15 Payroll Accounting,Odoo15 Payroll,Odoo 15,Payroll Accounting,Accounting""",
    'version': '15.0.1.0.0',
    'author': 'Fall Lewis YOMBA',
    'maintainer': 'Fall Lewis YOMBA',
    'depends': ['hr_payroll_community', 'account'],
    'data': ['views/hr_payroll_account_views.xml'],
    'test': ['../account/test/account_minimal_test.xml'],
    'demo': ['data/hr_payroll_account_demo.xml'],
    'license': 'AGPL-3',
}
