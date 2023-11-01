# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api

class low_stock_template(models.AbstractModel):

    _name = 'report.bi_product_low_stock_notification.low_stock_template'

    @api.model
    def _get_report_values(self, docids, data=None):
    	setting = self.env['res.config.settings'].search([],order="id desc",limit=1)

    	rec_ids = []
    	for rec in setting.low_stock_products_ids:
    		rec_ids.append(rec)

    	return {
            	'doc_ids': docids,
            	'data':data,
            	'docs':setting.id,
            	'rec_ids':rec_ids,
               }