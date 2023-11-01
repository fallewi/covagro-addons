# -*- coding: utf-8 -*-
{
	'name': 'Tableau de Bord COVAGRO',

	'summary': """
Tableau de Bord COVAGRO
""",

	'description': """
Tableau de Bord COVAGRO
""",

	'author': 'Fall Lewis YOMBA.',

	'license': 'OPL-1',

	'maintainer': 'Fall Lewis YOMBA.',

	'category': 'Tools',

	'version': '15.0.1.2.5',

	'depends': ['base', 'web', 'base_setup', 'bus'],

	'data': ['security/ir.model.access.csv', 'security/ks_security_groups.xml', 'data/ks_default_data.xml', 'views/ks_dashboard_ninja_view.xml', 'views/ks_dashboard_ninja_item_view.xml', 'views/ks_dashboard_action.xml', 'views/ks_import_dashboard_view.xml', 'wizard/ks_create_dashboard_wiz_view.xml', 'wizard/ks_duplicate_dashboard_wiz_view.xml'],

	'demo': ['demo/ks_dashboard_ninja_demo.xml'],

	'assets': {'web.assets_backend': ['ks_dashboard_ninja/static/src/css/ks_dashboard_ninja.scss', 'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_item.css', 'ks_dashboard_ninja/static/src/css/ks_icon_container_modal.css', 'ks_dashboard_ninja/static/src/css/ks_dashboard_item_theme.css', 'ks_dashboard_ninja/static/src/css/ks_dn_filter.css', 'ks_dashboard_ninja/static/src/css/ks_toggle_icon.css', 'ks_dashboard_ninja/static/src/css/ks_dashboard_options.css', 'ks_dashboard_ninja/static/src/js/ks_global_functions.js', 'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja.js', 'ks_dashboard_ninja/static/src/js/ks_to_do_dashboard.js', 'ks_dashboard_ninja/static/src/js/ks_filter_props.js', 'ks_dashboard_ninja/static/src/js/ks_color_picker.js', 'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_item_preview.js', 'ks_dashboard_ninja/static/src/js/ks_image_basic_widget.js', 'ks_dashboard_ninja/static/src/js/ks_dashboard_item_theme.js', 'ks_dashboard_ninja/static/src/js/ks_widget_toggle.js', 'ks_dashboard_ninja/static/src/js/ks_import_dashboard.js', 'ks_dashboard_ninja/static/src/js/ks_domain_fix.js', 'ks_dashboard_ninja/static/src/js/ks_quick_edit_view.js', 'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_kpi_preview.js', 'ks_dashboard_ninja/static/src/js/ks_date_picker.js', 'ks_dashboard_ninja/static/lib/css/gridstack.min.css', 'ks_dashboard_ninja/static/lib/js/gridstack-h5.js', 'ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js', 'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_pro.css', 'ks_dashboard_ninja/static/src/css/ks_to_do_item.css', 'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_graph_preview.js', 'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_list_view_preview.js', 'ks_dashboard_ninja/static/src/js/ks_to_do_preview.js'], 'web.assets_qweb': ['ks_dashboard_ninja/static/src/xml/**/*']},

	'uninstall_hook': 'uninstall_hook',
}
