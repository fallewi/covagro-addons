# -*- coding: utf-8 -*-
################################################################################# 
#
#    Author: Abdullah Khalil. Copyrights (C) 2022-TODAY reserved. 
#    Email: abdulah.khaleel@gmail.com
#    You may use this app as per the rules outlined in the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3. 
#    See <http://www.gnu.org/licenses/> for more detials.
#   
#
################################################################################# 

{
    'name': "Créer plusieurs Appel d'offre COVAGRO",   
    'summary': "Créer plusieurs Appel d'offre COVAGRO",   
    'description': """
       Créer plusieurs Appel d'offre COVAGRO
    """,   
    'author': "Fall Lewis YOMBA",
    'category': 'Purchase',
    'version': '15.0.0.0',
     "license": "LGPL-3",
    'depends': ['base','purchase','purchase_requisition'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invite_vendors_wizard_views.xml',
        'views/purchase_requisition_views.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
} 
