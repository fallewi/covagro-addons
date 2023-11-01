# See LICENSE file for full copyright and licensing details.
"""Fleet Tenant, Res Partner Model."""

from odoo import fields, models


class AccountInvoice(models.Model):
    """Account Invoice Model."""

    _inherit = "account.move"

    vehicle_service_id = fields.Many2one(
        'fleet.vehicle.log.services', string='Service de véhicule')
    is_invoice_receive = fields.Boolean(string="La facture de service est-elle reçue ?")
    is_invoice_return = fields.Boolean(string="Est-ce  le dépôt de la facture de service")
