# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api, _
from ast import literal_eval
from odoo import SUPERUSER_ID
import base64

class ResConfigSettings(models.TransientModel):
	_inherit = ['res.config.settings']


	@api.model 
	def default_get(self, flds): 
		result = super(ResConfigSettings, self).default_get(flds)

		context = self._context
		current_uid = context.get('uid')
		su_id = self.env['res.users'].browse(current_uid)        
		result['current_user'] = su_id.id
		return result

	notification_product_type = fields.Selection([('template','Product'),('variant','Product Variant')],related='company_id.notification_product_type',string='Apply On',readonly=False)

	notification_base = fields.Selection([('on_hand','On hand quantity'),('fore_cast','Forecast')],related='company_id.notification_base',string='Notification Based On',readonly=False)
	notification_products = fields.Selection([('for_all','Global for all product'),('fore_product',' Individual for all products'),('reorder',' Reorder Rules')],related='company_id.notification_products',string='Min Quantity Based On',readonly=False)
	min_quantity = fields.Float(string = 'Quantity Limit',related='company_id.min_quantity',readonly=False)
	email_user = fields.Char( string="Email From",related='company_id.email',readonly=False) 
	low_stock_products_ids = fields.One2many('low.stock.transient','stock_product_id',store=True)
	value = fields.Char(string="Value",default= "Value")
	current_user = fields.Many2one('res.users',string='current')


	def set_values(self):
		super(ResConfigSettings, self).set_values()
		context = self._context
		current_uid = context.get('uid')
		su_id = self.env['res.users'].browse(current_uid)        
		self.current_user = su_id.id
		self.env['ir.config_parameter'].sudo().set_param('bi_product_low_stock_notification.current_user', self.current_user)
	
	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		res.update({
			'current_user':self.env['ir.config_parameter'].sudo().get_param('bi_product_low_stock_notification.current_user'),})
		return res

	def action_list_products_(self):
		products_list=[]
		
		res = self.env['res.config.settings'].search([],order="id desc", limit=1)
		if res.id :
			products_dlt = [(2,dlt.id,0)for dlt in res.low_stock_products_ids]
			res.low_stock_products_ids = products_dlt

			if res.notification_base == 'on_hand':
				if res.notification_products == 'for_all':

					if res.notification_product_type == 'variant':
						result = self.env['product.product'].search([('qty_available','<',res.min_quantity)])

						for product in result:
							name_att = ' '
							for attribute in product.product_template_attribute_value_ids:
								name_att = name_att  +  attribute.name + '  '

							name_pro = ' '
							if product.product_template_attribute_value_ids :
								name_pro = product.name + ' - ' +name_att + '  '
							else :
								name_pro = product.name

							products_list.append([0,0,{'name':name_pro,
													'limit_quantity':res.min_quantity,
													'stock_quantity':product.qty_available}])
					else:
						result = self.env['product.template'].search([])
						for product in result:
							if product.qty_available < res.min_quantity:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':res.min_quantity,
													'stock_quantity':product.qty_available}])

				if res.notification_products == 'fore_product':

					if res.notification_product_type == 'variant':                  
						result = self.env['product.product'].search([])

						for product in result:
							if product.qty_available < product.min_quantity:
								name_att = ' '
								for attribute in product.product_template_attribute_value_ids:
									name_att = name_att  +  attribute.name + '  '

								name_pro = ' '
								if product.product_template_attribute_value_ids :
									name_pro = product.name + ' - ' +name_att + '  '
								else :
									name_pro = product.name

								products_list.append([0,0,{'name':name_pro,
															'limit_quantity':product.min_quantity,
														'stock_quantity':product.qty_available}])
					else:
						result = self.env['product.template'].search([])

						for product in result:
							if product.qty_available < product.temp_min_quantity:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':product.temp_min_quantity,
													'stock_quantity':product.qty_available}])

				if res.notification_products == 'reorder':

					if res.notification_product_type == 'variant':                  
						result = self.env['product.product'].search([])
						for product in result:
							if product.qty_available < product.qty_min:
								name_att = ' '
								for attribute in product.product_template_attribute_value_ids:
									name_att = name_att  +  attribute.name + '  '

								name_pro = ' '
								if product.product_template_attribute_value_ids :
									name_pro = product.name + ' - ' +name_att + '  '
								else :
									name_pro = product.name
								vals = {'name':name_pro,
										'limit_quantity':product.qty_min,
										'stock_quantity':product.qty_available}

								products_list.append([0,0,vals])

					else:
						result = self.env['product.template'].search([])

						for product in result:
							if product.qty_available < product.temp_qty_min:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':product.temp_qty_min,
													'stock_quantity':product.qty_available}])

			if res.notification_base=='fore_cast':
				if res.notification_products=='for_all':

					if res.notification_product_type == 'variant':
						result = self.env['product.product'].search([('virtual_available','<',res.min_quantity)])
						for product in result:
							name_att = ' '
							for attribute in product.product_template_attribute_value_ids:
								name_att = name_att  +  attribute.name + '  '

							name_pro = ' '
							if product.product_template_attribute_value_ids :
								name_pro = product.name + ' - ' +name_att + '  '

							else :
								name_pro = product.name

							products_list.append([0,0,{'name':name_pro,
													'limit_quantity':res.min_quantity,
													'stock_quantity':product.virtual_available}])
					else:
						result = self.env['product.template'].search([])

						for product in result:
							if product.virtual_available < res.min_quantity:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':res.min_quantity,
													'stock_quantity':product.virtual_available}])


				if res.notification_products == 'fore_product':
					
					if res.notification_product_type == 'variant':
						result = self.env['product.product'].search([])

						for product in result:
							if product.virtual_available < product.min_quantity:
								name_att = ' '
								for attribute in product.product_template_attribute_value_ids:
									name_att = name_att  +  attribute.name + '  '

								name_pro = ' '
								if product.product_template_attribute_value_ids :
									name_pro = product.name + ' - ' +name_att + '  '
								else :
									name_pro = product.name
								products_list.append([0,0,{'name':name_pro,
															'limit_quantity':product.min_quantity,
														'stock_quantity':product.virtual_available}])
					
					else:
						result = self.env['product.template'].search([])

						for product in result:
							if product.virtual_available < product.temp_min_quantity:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':product.temp_min_quantity,
													'stock_quantity':product.virtual_available}])

				if res.notification_products == 'reorder':

					if res.notification_product_type == 'variant':                  
						result = self.env['product.product'].search([])
						for product in result:
							if product.qty_available < product.qty_min:
								name_att = ' '
								for attribute in product.product_template_attribute_value_ids:
									name_att = name_att  +  attribute.name + '  '

								name_pro = ' '
								if product.product_template_attribute_value_ids :
									name_pro = product.name + ' - ' +name_att + '  '
								else :
									name_pro = product.name

								products_list.append([0,0,{'name':name_pro,
															'limit_quantity':product.qty_min,
														'stock_quantity':product.qty_available}])
					else:
						result = self.env['product.template'].search([])

						for product in result:
							if product.qty_available < product.temp_qty_min:
								products_list.append([0,0,{'name':product.name,
													'limit_quantity':product.temp_qty_min,
													'stock_quantity':product.qty_available}])

			res.low_stock_products_ids = products_list
			return 
		else :
			return
		
	def action_low_stock_send(self):
		context = self._context
		current_uid = context.get('uid')
		su_id = self.env['res.users'].browse(current_uid)
		self.action_list_products_()
		company = self.env['res.company'].search([('notify_low_stock','=',True)])
		res = self.env['res.config.settings'].search([],order="id desc", limit=1)
		if su_id :
			current_user = su_id
		else:
			current_user = res['current_user']
		if res.id :
			if res.low_stock_products_ids:
				if company:
					for company_is in company:

						template_id = self.env['ir.model.data'].get_object_reference('bi_product_low_stock_notification','low_stock_email_template')[1]
						email_template_obj = self.env['mail.template'].browse(template_id)
						if template_id:
							
							values = email_template_obj.generate_email(res.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
							values['email_from'] = current_user.email
							values['email_to'] = company_is.email
							values['author_id'] = current_user.partner_id.id
							values['res_id'] = False
							pdf = self.env.ref('bi_product_low_stock_notification.action_low_stock_report')._render([res.id])[0]
							values['attachment_ids'] = [(0,0,{
								'name': 'Product Low Stock Report',
								'datas': base64.b64encode(pdf),
								'res_model': res._name,
								'res_id': res.id,
								'mimetype': 'application/x-pdf',
								'type': 'binary',
								})]
							mail_mail_obj = self.env['mail.mail']
							msg_id = mail_mail_obj.create(values)
							if msg_id:
								msg_id.send()

				for partner in self.env['res.users'].search([]):
					if partner.notify_user:
						template_id = self.env['ir.model.data'].get_object_reference('bi_product_low_stock_notification','low_stock_email_template')[1]
						email_template_obj = self.env['mail.template'].browse(template_id)
						if template_id:
							values = email_template_obj.generate_email(res.id,['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
							values['email_from'] = current_user.email
							values['email_to'] = partner.email
							values['author_id'] = current_user.partner_id.id
							values['res_id'] = False
							pdf = self.env.ref('bi_product_low_stock_notification.action_low_stock_report')._render([res.id])[0]
							values['attachment_ids'] = [(0,0,{
								'name': 'Product Low Stock Report',
								'datas': base64.b64encode(pdf),
								'res_model': res._name,
								'res_id': res.id,
								'mimetype': 'application/x-pdf',
								'type': 'binary',
								})]
							mail_mail_obj = self.env['mail.mail']
							msg_id = mail_mail_obj.create(values)
							if msg_id:
								msg_id.send()

		return True
	


class low_stock_product(models.TransientModel):
	_name='low.stock.transient'

	name=fields.Char(string='Product name')
	stock_quantity=fields.Float(string='Quantity')
	limit_quantity=fields.Float(string='Quantity limit')
	stock_product_id=fields.Many2one('res.config.settings')

