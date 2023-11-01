# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Company(models.Model):
    _inherit = 'res.company'

    process_costing = fields.Selection([('manually', 'Manually'), ('workcenter', 'Work-Center')],
                                       string="Méthode d'établissement des coûts de processus", default="manually")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    process_costing = fields.Selection(string="Méthode d'établissement des coûts de processus", related="company_id.process_costing",
                                       readonly=False)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    labour_costs_hour = fields.Float(string='Coûts de main-d\'œuvre par heure', help="Spécifiez le coût de la main-d'œuvre par heure.",
                                     default=0.0)
    overhead_cost_hour = fields.Float(string="Frais généraux par heure", help="Spécifiez le coût des frais généraux par heure.",
                                      default=0.0)
