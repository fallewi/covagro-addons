# See LICENSE file for full copyright and licensing details.
"""Analysis report for the shipping operations."""

from odoo import fields, models, tools


class ShippingOperationReport(models.Model):
    """Shipping operation Report Model."""

    _name = "shipping.operation.report"
    _description = "Rapport d'opération d'expédition"
    _auto = False

    name = fields.Char(string="Nom", readonly=1)
    customer_id = fields.Many2one("res.partner", string="Client", readonly=1)
    agent_id = fields.Many2one("res.partner", string="Agent", readonly=1)
    loading_port_id = fields.Many2one("freight.port", string="Port de chargement", readonly=1)
    discharg_port_id = fields.Many2one(
        "freight.port", string="Port de décharge", readonly=1
    )
    direction = fields.Selection(
        [("import", "Importation"), ("export", "Exportation")], string="Direction", readonly=1
    )
    transport = fields.Selection(
        [("land", "Terrestre"), ("ocean", "Marin"), ("air", "Aérien")],
        string="Transport",
        readonly=1,
    )
    order_date = fields.Datetime(string="Date de commande", readonly=1)
    inv_payment = fields.Float(string="Montant de la facture", readonly=1)
    bill_payment = fields.Float(string="Montant de la facture", readonly=1)

    # @api.model_cr
    def init(self):
        """Initalization method."""
        tools.drop_view_if_exists(self.env.cr, "shipping_operation_report")
        self.env.cr.execute(
            """create or replace view shipping_operation_report
            as (select id as id,
            name as name,
            customer_id as customer_id,
            agent_id as agent_id,
            loading_port_id as loading_port_id,
            discharg_port_id as discharg_port_id,
            direction as direction,
            transport as transport,
            order_date as order_date,
            (select sum(amount_total) from account_move \
            where operation_id=freight_operation.id and \
                move_type='out_invoice') as inv_payment,
                (select sum(amount_total) from account_move where
                operation_id=freight_operation.id and \
                move_type='in_invoice') as bill_payment
            from freight_operation)"""
        )
