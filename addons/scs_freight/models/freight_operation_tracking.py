# See LICENSE file for full copyright and licensing details.
"""This module contains freight operations."""

from odoo import fields, models


class OperationTracking(models.Model):
    """Track the Freight Operation."""

    _name = "operation.tracking"
    _description = "Détail pour suivre la commande"

    source_location_id = fields.Many2one("freight.port", string="Emplacement de la source")
    dest_location_id = fields.Many2one("freight.port", string="Emplacement de destination")
    date = fields.Date(string="Date")
    activity = fields.Char(string="Activité")
    operation_id = fields.Many2one("freight.operation", string="Operation")
