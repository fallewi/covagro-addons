# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTriggerProductLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_line"
    _description = "Gamme de produits déclencheurs de contrôle de la qualité"

    product = fields.Many2one(comodel_name="product.product")

    def get_trigger_line_for_product(self, trigger, product, partner=False):
        trigger_lines = super().get_trigger_line_for_product(
            trigger, product, partner=partner
        )
        for trigger_line in product.qc_triggers.filtered(
            lambda r: r.trigger == trigger
            and (
                not r.partners
                or not partner
                or partner.commercial_partner_id in r.partners
            )
            and r.test.active
        ):
            trigger_lines.add(trigger_line)
        return trigger_lines
