# See LICENSE file for full copyright and licensing details.
"""This module contain feright operations."""

from odoo import fields, models


class IrAttachment(models.Model):
    """Attachment Model."""

    _inherit = "ir.attachment"

    custom_id = fields.Many2one("operation.custom", string="Opération")
