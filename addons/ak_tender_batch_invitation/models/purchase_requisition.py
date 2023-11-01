# -*- coding: utf-8 -*-

from hashlib import new
from odoo import models, fields, api, _

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    partner_ids = fields.One2many('requisition.vendor', 'requisition_id', string='Fournisseurs')
    

class RequisitionVendors(models.Model):
    _name = 'requisition.vendor'

    partner_id = fields.Many2one('res.partner', string="Fournisseur")
    requisition_id = fields.Many2one('purchase.requisition', string="Réquisition")
    invitation_state = fields.Selection([
        ('new', 'Nouveau'),
        ('sent', 'Appel d\'offre'),
        ('sent_with_email', 'Appel d\'offre envoyé'),
    ], string="Statut de l'invitation ", default="new", required=True)
    purchase_order_id = fields.Many2one('purchase.order', string="Appel d'offre COVAGRO", readonly=True)

