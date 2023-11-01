from . import models
from odoo.api import Environment, SUPERUSER_ID

def ks_dna_uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    for rec in env['ks_dashboard_ninja.item'].search([]):
        if rec.ks_data_calculation_type == 'query':
            rec.unlink()
