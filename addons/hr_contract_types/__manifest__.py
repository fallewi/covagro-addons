# -*- coding: utf-8 -*-

{
    'name': 'Type de contrat d\enployés COVAGRO',
    'version': '15.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """
        Contract type in contracts
    """,
    'description': """Type de contrat d\enployés COVAGRO""",
    'author': 'Fall Lewis YOMBA',
    'depends': ['hr', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'data/hr_contract_type_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}