"""Inherited Res Partner Model."""
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """Inherit Partner Model."""

    _inherit = "res.partner"

    agent = fields.Boolean(string="Est un agent?")
