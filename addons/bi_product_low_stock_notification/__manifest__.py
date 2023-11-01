 # -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Product Low Stock Notification/Alert in odoo',
	'version': '14.0.0.0',
	'category': 'Inventory',
	'sequence':140 ,
	"price": 19,
	"currency": 'EUR',
	'summary': 'Apps for Product low stock alerts on product minimum stock alerts on product low stock notification on product stock alerts warehouse low stock alerts Print product Low Stock Report Minimum Stock Reminder Email Stock notify Email product stock alert',
	'description': """To send notification to user while stock is low
		This apps help to receive low stock notification about product when product stock goes below on certian stock 
		product low stock notification Low Stock alert in odoo ,  Out of Stock Notification , Email Notification On Low stock, Out of stock , Back to stock
		product low stock notify in odoo
		product low stock alerts , inventory notifier
		product low stock alarm
		email notificaion about low stock products
		Minimum Stock Reminder Email
		Stock Reminder Email
		Stock notify Email
		Print Low Stock Report
		Low Stock Report
		configurable low stock for product , send email notification for low stock product
		product stock alerts
		product stock notification
		product stock alarm
		Minimum Stock Reminder Notifications by Product
		product stock email notification
		low product stock notification
		low stock product notification
		low stock product alert
		alert low stock product
		alert stock low product
		stock alert
		low stock alert
		inventory alert
		Stock Notification

		product stock alerts
		minimum product stock alerts
		minimum product stock notification
		warehouse stock alerts
		warehouse stock notification
		warehouse stock alarms
		warehouse product stock alerts
		warehouse product stock notification
		warehouse product stock alarms

		warehouse low stock alerts
		warehouse low stock notification
		warehouse low stock alarms
		warehouse low product stock alerts
		warehouse low product stock notification
		warehouse low product stock alarms
		warehouse minimum stock alerts
		warehouse minimum stock notification
		warehouse minimum stock alarms
		warehouse minimum product stock alerts
		warehouse minimum product stock notification
		warehouse minimum product stock alarms
	""",
	'author':'Browseinfo',
	'website': 'https://www.browseinfo.in',
	'depends': ['base','sale_management','stock'],
	'data': [
	'security/ir.model.access.csv',
	'view/product_product_view.xml',
	'report/low_stock_report_template.xml',
	'view/email_templete.xml',
	'view/stock_config_settings_views.xml',
	'data/low_stock_notification_cron.xml',
	'view/inherited_res_users.xml',
			
	],
	
	'test': [],
		
	
	'demo': [],
	'css': [],
	'installable': True,
	'auto_install': False,
	'application': False,
	'live_test_url':'https://youtu.be/Zphh2zyzluY',
	"images":['static/description/Banner.png'],
}


