# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Type de contrat'
    _order = 'sequence, id'

    name = fields.Char(string='Type de contrat', required=True, help="Name")
    sequence = fields.Integer(help="Donne la séquence lors de l'affichage d'une liste de Contrat.", default=10)


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one('hr.contract.type', string="Catégorie d'employé",
                              required=True, help="Catégorie d'employé",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
