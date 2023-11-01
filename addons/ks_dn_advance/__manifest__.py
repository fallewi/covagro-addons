# -*- coding: utf-8 -*-
{
	'name': 'Tableau de Bord Graphique COVAGRO',


    'summary': """
       Tableau de Bord Graphique COVAGRO
    """,


	'description': """
Tableau de Bord Graphique COVAGRO
""",

	'author': 'Fall Lewis YOMBA.',

	'license': 'OPL-1',


	'maintainer': 'Fall Lewis YOMBA.',


	'category': 'Tools',

	'version': '15.0.1.1.1',


	'depends': ['ks_dashboard_ninja'],

	'data': ['views/ks_dashboard_ninja_item_view_inherit.xml',
			 'views/ks_dashboard_form_view_inherit.xml',
			 'views/ks_mail_template.xml'],

	'assets': {'web.assets_backend': ['ks_dn_advance/static/src/css/ks_tv_dashboard.css', 'ks_dn_advance/static/lib/css/owl.carousel.min.css','ks_dn_advance/static/src/js/ks_dn_kpi_preview.js', 'ks_dn_advance/static/src/js/ks_labels.js', 'ks_dn_advance/static/src/js/ks_ylabels.js', 'ks_dn_advance/static/src/js/ks_dashboard_ninja_tv_graph_preview.js', 'ks_dn_advance/static/src/js/ks_dashboard_ninja_tv_list_preview.js', 'ks_dn_advance/static/src/js/ks_tv_dashboard.js', 'ks_dn_advance/static/lib/js/owl.carousel.min.js', 'ks_dn_advance/static/lib/js/print.min.js', 'ks_dn_advance/static/lib/js/pdf.min.js'], 'web.assets_frontend': ['ks_dn_advance/static/src/css/ks_tv_dashboard.css', 'ks_dn_advance/static/src/js/ks_website_dashboard.js'], 'web.assets_qweb': ['ks_dn_advance/static/src/xml/**/*']},

	'uninstall_hook': 'ks_dna_uninstall_hook',
}
