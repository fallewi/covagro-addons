# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Coût de fabrication COVAGRO',
    'version': '15.0.0.4',
    'category': 'Manufacturing',
    'description': """
       Coût de fabrication COVAGRO

""",
    'author': 'Fall Lewis YOMBA',
    'category': 'Manufacturing',
    'depends': ['sale_management', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_bom_view.xml',
        'views/config.xml',
        'report/mrp_costing_report.xml',
        'report/mrp_bom_report_view.xml',
        'report/mrp_production_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
