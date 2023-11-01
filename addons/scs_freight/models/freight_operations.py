# See LICENSE file for full copyright and licensing details.
"""This module contain freight operations."""

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class FreightOperation(models.Model):
    """Freight Operation Model."""

    _name = "freight.operation"
    _description = "Opérations de fret"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Nom", copy=False, required=True, readonly=True, default=lambda self: _('New'))
    folder_id = fields.Many2one(comodel_name='freight.folder', string='File', required=False)
    direction = fields.Selection(
        [("import", "Importation"), ("export", "Exportation")],
        string="Direction",
        default="import",
    )
    transport = fields.Selection(
        [("land", "Terrestre"), ("ocean", "Marin"), ("air", "Aérien")],
        default="land",
        string="Transport",
    )
    ocean_shipping = fields.Selection(
        [("fcl", "FCL"), ("lcl", "LCL")],
        string="Transport maritime",
        help="""FCL: Full Container Load.
        LCL: Less Container Load.""",
    )
    land_shipping = fields.Selection(
        [("ftl", "FTL"), ("ltc", "LTL")],
        string="Transport terrestre",
        help="""FTL: Full Truckload.
        LTL: Less Then Truckload.""",
    )
    customer_id = fields.Many2one("res.partner", string="Client")
    consignee_id = fields.Many2one("res.partner", string="Destinataire")
    operator_id = fields.Many2one(
        "res.users", string="Operateur", default=lambda self: self.env.user.id
    )
    loading_port_id = fields.Many2one("freight.port", string="Port de chargement")
    discharg_port_id = fields.Many2one("freight.port", string="Port de décharge")
    voyage_no = fields.Char(string="Voyage No")
    vessel_id = fields.Many2one(
        "freight.vessels", string="Navire", domain="[('transport', '=', transport)]"
    )
    airline_id = fields.Many2one("freight.airline", string="Air Line")
    note = fields.Text(string="Notes")
    agent_id = fields.Many2one("res.partner", string="Agent")
    incoterm_from = fields.Many2one("freight.incoterm", string="De")
    incoterm_to = fields.Many2one("freight.incoterm", string="A")
    master_awb = fields.Char("Master AWB")
    house_awb = fields.Char("House AWB")
    master_bl = fields.Char("Master BL")
    house_bl = fields.Char("House BL")
    master_lt = fields.Char("Master LT")
    house_lt = fields.Char("House LT")

    operation_line_ids = fields.One2many(
        "freight.operation.line", "operation_id", string="Commande", copy=False
    )
    routes_ids = fields.One2many("operation.route", "operation_id", string="Routes")
    service_ids = fields.One2many(
        "operation.service", "operation_id", string="Services"
    )
    commercial_invoices_ids = fields.One2many(
        "operation.commercial.invoice", "operation_id", string="Factures commerciales"
    )
    tracking_ids = fields.One2many(
        "operation.tracking", "operation_id", string="Suivis"
    )
    container_ids = fields.One2many("freight.offer.cargaison", "operation_id", string="Type d'emballage", copy=False)

    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("confirm", "Confirmé"),
            ("in_progress", "En cours de progression"),
            ("custom", "Customisé"),
            ("in_transit", "En transit"),
            ("recived", "Reçu"),
            ("delivered", "Livré"),
            ("cancel", "Annulé"),
        ],
        default="draft",
        string="Statut",
    )
    invoicing_state = fields.Selection(
        [
            ("nothing", "Rien à facturer"),
            ("ready", "Prêt à facturer"),
            ("invoiced", "Facturé"),
        ],
        default="nothing",
        string="Statut de facturation",
        compute="_compute_financial_state"
    )
    billing_state = fields.Selection(
        [
            ("nothing", "Rien à facturer"),
            ("ready", "Prêt à facturer"),
            ("billed", "Facturé"),
        ],
        default="nothing",
        string="Statut de facturation",
        compute="_compute_financial_state"
    )
    order_date = fields.Datetime(string="Date de commande", default=datetime.now())
    company_id = fields.Many2one(
        "res.company", string="Entreprise", default=lambda self: self.env.company.id
    )
    exp_send_date = fields.Date(string="Heure de départ estimée", help="Date d'envoi prévue")
    act_send_date = fields.Date(string="Heure de départ réelle ", help="Date d'envoi réelle")
    exp_rec_date = fields.Date(string="Temps d'arrivée estimé")
    act_rec_date = fields.Date(string="Heure de départ réelle")
    opp_party_id = fields.Many2one("res.partner", string="Party")
    invoice_id = fields.Many2one("account.move", string="Facture", copy=False)
    bill_id = fields.Many2one("account.move", string="Bill")
    exp_inv_payment = fields.Float(string="Montant de la vente", compute="_compute_expected_receivable_payment")
    exp_bill_payment = fields.Float(
        string="Montant du coût", compute="_compute_expected_payable_payment"
    )
    exp_payment_margin = fields.Float(
        compute="_compute_exp_payment_margin", string="Expected Margin"
    )
    act_inv_payment = fields.Float(
        string="Paiement à recevoir réel",
        compute="_compute_actual_receivable_payment",
        help="Paiement à recevoir réel",
    )
    act_bill_payment = fields.Float(
        string="Act Pay Payment",
        compute="_compute_actual_payable_payment",
        help="Paiement réel à payer",
    )
    act_payment_margin = fields.Float(
        string="Marge réelle", compute="_compute_act_payment_margin"
    )
    inv_amount_due = fields.Float(
        compute="_compute_inv_amount_due", string="Montant de la facture due"
    )
    bill_amount_due = fields.Float(
        compute="_compute_bill_amount_due", string="Montant de la facture due"
    )
    total_service = fields.Integer(
        string="Services totaux", compute="_compute_total_services"
    )
    total_custom = fields.Integer(
        string="Dédouanement", compute="_compute_total_custom"
    )
    total_weight = fields.Float(
        string="Poids total", store=True, compute="_compute_weight_and_volume"
    )
    total_volume = fields.Float(
        string="Volume total", store=True, compute="_compute_weight_and_volume"
    )
    bill_count = fields.Integer(compute="_compute_count_bill", string="La facture compte")
    invoice_count = fields.Integer(
        compute="_compute_count_bill", string="Comptes de facture"
    )
    service_count = fields.Integer(compute="_compute_count_bill")

    def _compute_count_bill(self):
        """Method to count Invoice, Bill and Service."""
        account_move_obj = self.env["account.move"]
        operation_obj = self.env["operation.service"]
        for operation in self:
            operation.bill_count = account_move_obj.search_count(
                [("operation_id", "=", operation.id), ("move_type", "=", "in_invoice")]
            )
            operation.invoice_count = account_move_obj.search_count(
                [("operation_id", "=", operation.id), ("move_type", "=", "out_invoice")]
            )
            operation.service_count = operation_obj.search_count(
                [("operation_id", "=", operation.id)]
            )

    @api.constrains(
        "order_date", "exp_send_date", "act_send_date", "exp_rec_date", "act_rec_date"
    )
    def _check_date(self):
        for operation in self:
            order_date = operation.order_date and operation.order_date.date()
            if operation.exp_send_date and operation.exp_send_date < order_date:
                raise UserError(
                    _(
                        "La date d'envoi prévue doit être supérieure ou "
                        "est égal à la date de commande !!"
                    )
                )
            elif operation.act_send_date and operation.act_send_date < order_date:
                raise UserError(
                    _(
                        "La date d'envoi réelle doit être supérieure ou"
                        "est égal à la date de commande !!"
                    )
                )
            elif operation.exp_rec_date and operation.exp_rec_date < order_date:
                raise UserError(
                    _(
                        "La date de réception prévue doit être supérieure ou"
                        " est égal à la date de commande !!"
                    )
                )
            elif operation.act_rec_date and operation.act_rec_date < order_date:
                raise UserError(
                    _(
                        "La date de réception réelle doit être supérieure ou"
                        " est égal à la date de commande !!"
                    )
                )

    @api.constrains("loading_port_id", "discharg_port_id")
    def _check_loading_discharging_port(self):
        for operation in self:
            if (
                    operation.loading_port_id
                    and operation.discharg_port_id
                    and operation.loading_port_id.id == operation.discharg_port_id.id
            ):
                raise UserError(
                    _("Le port de chargement et le port de déchargement doivent être différents !!")
                )

    @api.constrains("operation_line_ids")
    def _check_container_capacity(self):
        for operation in self:
            for line in operation.operation_line_ids:
                containers = operation.operation_line_ids.filtered(
                    lambda rec: rec.container_id.id == line.container_id.id
                )
                order_weight = order_volume = 0.0
                for container in containers:
                    order_weight += container.exp_gross_weight or 0.0
                    order_volume += container.exp_vol or 0.0
                if order_weight > line.container_id.weight:
                    raise UserError(
                        _(
                            "[ %s ] La capacité de poids du conteneur est"
                            " %s !\n Vous avez prévu plus de poids que la capacité du conteneur "
                            "!!"
                        )
                        % (line.container_id.name, line.container_id.weight)
                    )

                if order_volume > line.container_id.volume:
                    raise UserError(
                        _(
                            "%s La capacité de volume du conteneur est %s !"
                            "\n Vous avez prévu plus de volume que la capacité du conteneur "
                            "!!"
                        )
                        % (line.container_id.name, line.container_id.volume)
                    )

    @api.onchange("discharg_port_id", "transport")
    def _check_port_type(self):
        for operation in self:
            if operation.discharg_port_id and operation.transport:
                if operation.transport == "land":
                    if not operation.discharg_port_id.is_land:
                        raise UserError(
                            _("%s le port n'a pas de voie terrestre!")
                            % operation.discharg_port_id.name
                        )
                elif operation.transport == "ocean":
                    if not operation.discharg_port_id.is_ocean:
                        raise UserError(
                            _("%s le port n'a pas de route maritime!")
                            % operation.discharg_port_id.name
                        )
                elif operation.transport == "air":
                    if not operation.discharg_port_id.is_air:
                        raise UserError(
                            _("%s le port n'a pas de route aérienne !")
                            % operation.discharg_port_id.name
                        )

    @api.onchange("customer_id")
    def _onchange_customer_id(self):
        """Onchange to set the consignee_id."""
        for operation in self:
            operation.consignee_id = (operation.customer_id and operation.customer_id.id or False)

    def _compute_expected_receivable_payment(self):
        """Calculate the total invoice amount."""
        for operation in self:
            invs = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            operation.exp_inv_payment = sum(invs.mapped("amount_total")) or 0.0

    def _compute_expected_payable_payment(self):
        """Calculate expected payable amount of Bill."""
        for operation in self:
            bills = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            operation.exp_bill_payment = sum(bills.mapped("amount_total")) or 0.0

    def _compute_financial_state(self):
        """Calculate expected payable amount of Bill."""
        for operation in self:
            invs = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            if not len(operation.service_ids):
                operation.invoicing_state = "nothing"
            elif not len(invs) or len(invs) < len(operation.service_ids):
                operation.invoicing_state = "ready"
            else:
                operation.invoicing_state = "invoiced"

            bills = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            if not len(operation.service_ids):
                operation.billing_state = "nothing"
            elif not len(bills) or len(bills) < len(operation.service_ids):
                operation.billing_state = "ready"
            else:
                operation.billing_state = "billed"

    def _compute_act_payment_margin(self):
        """Actual Payment Margin.

        act_inv_payment - act_bill_payment = margin
        """
        for operation in self:
            operation.act_payment_margin = (
                    operation.act_inv_payment - operation.act_bill_payment
            )

    def _compute_exp_payment_margin(self):
        """Expected Payment Margin.

        exp_inv_payment - exp_bill_payment = margin
        """
        for operation in self:
            operation.exp_payment_margin = (
                    operation.exp_inv_payment - operation.exp_bill_payment
            )

    def _compute_actual_receivable_payment(self):
        """Calculate Actual Receivable(Invoice) Payment."""
        for operation in self:
            invs = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            total = sum(inv.amount_total - inv.amount_residual for inv in invs) or 0.0
            operation.act_inv_payment = total

    def _compute_actual_payable_payment(self):
        """Calculate actual Payable(Bill) Payment."""
        for operation in self:
            bills = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            total = sum(bill.amount_total - bill.amount_residual for bill in bills) or 0.0
            operation.act_bill_payment = total

    def _compute_inv_amount_due(self):
        """Count Remaining invoice amount."""
        for operation in self:
            invs = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            operation.inv_amount_due = sum(invs.mapped("amount_residual")) or 0.0

    def _compute_bill_amount_due(self):
        """Count Remaining Bill amount."""
        for operation in self:
            bills = self.env["account.move"].search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "not in", ["cancel"]),
                ]
            )
            operation.bill_amount_due = sum(bills.mapped("amount_residual")) or 0.0

    def _compute_total_services(self):
        for operation in self:
            operation.total_service = self.env["operation.service"].search_count(
                [("operation_id", "=", operation.id)]
            )

    def _compute_total_custom(self):
        for operation in self:
            operation.total_custom = self.env["operation.custom"].search_count(
                [("operation_id", "=", operation.id)]
            )

    @api.depends("operation_line_ids")
    def _compute_weight_and_volume(self):
        freight_line_obj = self.env["freight.operation.line"]
        for operation in self:
            freight_op_line_recs = freight_line_obj.search_read(
                [("operation_id", "=", operation.id)]
            )
            operation.total_weight = sum(
                weight.get("exp_gross_weight", 0.0) for weight in freight_op_line_recs
            )
            operation.total_volume = sum(
                volume.get("exp_vol", 0.0) for volume in freight_op_line_recs
            )

    @api.model
    def create(self, vals):
        """Base ORM Method."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.operation.direct') or _('New')
        rec = super(FreightOperation, self).create(vals)
        '''
        if not vals.get("operation_line_ids", False):
            raise UserError(
                _(
                    "Vous ne pouvez pas créer ou dupliquer "
                    "une expédition directe sans lignes de commande !!"
                )
            )
        '''
        return rec

    def write(self, vals):
        """Overridden write Method."""
        rec = super(FreightOperation, self).write(vals)
        for freight in self:
            for route in freight.routes_ids:
                if route.service_ids:
                    route.service_ids.write({"operation_id": freight.id})
        return rec

    def unlink(self):
        """ORM Method delete the record."""
        for operation in self:
            if operation.state not in ["draft", "cancel"]:
                raise UserError(
                    _(
                        "Vous ne pouvez pas supprimer cette opération d'expédition.\n"
                        "Veuillez le définir sur Annuler avant de supprimer."
                    )
                )
        return super(FreightOperation, self).unlink()

    def action_confirm(self):
        """Action Confirm Method."""
        for operation in self:
            operation_vals = {

            }
            for line in operation.operation_line_ids:
                if line.exp_vol > line.container_id.volume:
                    raise UserError(
                        _(
                            "%s La capacité de volume du conteneur est %s !!\n"
                            "Vous avez prévu plus de volume que la capacité du conteneur"
                            "!!"
                        )
                        % (line.container_id.name, line.container_id.volume)
                    )
                if line.exp_gross_weight > line.container_id.weight:
                    raise UserError(
                        _(
                            "%s La capacité de poids du conteneur est %s !!\n"
                            "Vous avez prévu plus de poids que la capacité du conteneur"
                            "!!"
                        )
                        % (line.container_id.name, line.container_id.weight)
                    )
            route_val = {
                "route_operation": "main_carrige",
                "source_location": operation.loading_port_id
                                   and operation.loading_port_id.id
                                   or False,
                "dest_location": operation.discharg_port_id
                                 and operation.discharg_port_id.id
                                 or False,
                "transport": operation.transport,
            }
            operation_vals.update(
                {"state": "confirm", "routes_ids": [(0, 0, route_val)]}
            )
            operation.write(operation_vals)
            containers = operation.operation_line_ids.mapped("container_id")

            services = operation.mapped("routes_ids").mapped("service_ids")
            if services:
                services.write({"operation_id": operation.id})

    def action_cancel(self):
        """Cancel the Freight Operation."""
        for operation in self:
            operation.write({"state": "cancel"})
            containers = operation.operation_line_ids.mapped("container_id")
            if containers:
                containers.write({"state": "available"})

    def action_set_to_draft(self):
        """Set freight operation in 'draft' state."""
        inv_obj = self.env["account.move"]
        for operation in self:
            invs = inv_obj.search(
                [
                    ("operation_id", "=", operation.id),
                    ("state", "in", ["draft", "cancel"]),
                ]
            )
            invs.unlink()
            operation.write(
                {
                    "state": "draft",
                    "act_inv_payment": 0.0,
                    "act_bill_payment": 0.0,
                    "inv_amount_due": 0.0,
                    "bill_amount_due": 0.0,
                    "routes_ids": [],
                    "tracking_ids": [],
                    "service_ids": [],
                }
            )
            containers = operation.operation_line_ids.mapped("container_id")
            if containers:
                containers.write({"state": "available"})
            if operation.service_ids:
                operation.service_ids.write(
                    {
                        "invoice_id": False,
                        "inv_line_id": False,
                        "bill_id": False,
                        "bill_line_id": False,
                    }
                )

    def action_invoice(self):
        """Create Invoice for the freight operation."""
        inv_obj = self.env["account.move"]
        for operation in self:
            services = operation.mapped("routes_ids").mapped("service_ids")
            services.write({"operation_id": operation.id})
            invoice = inv_obj.search(
                [
                    ("operation_id", "=", operation.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "draft"),
                    (
                        "partner_id",
                        "=",
                        operation.consignee_id and operation.consignee_id.id or False,
                    ),
                ],
                limit=1,
            )
            done_line = operation.operation_line_ids.mapped("invoice_id")
            done_services = operation.service_ids.mapped("invoice_id")
            if len(done_line) < len(operation.operation_line_ids) or len(
                    done_services
            ) < len(operation.service_ids):
                if not invoice:
                    inv_val = {
                        "operation_id": operation.id or False,
                        "move_type": "out_invoice",
                        "state": "draft",
                        "partner_id": operation.consignee_id.id or False,
                        "invoice_date": fields.Date.context_today(self),
                    }
                    invoice = inv_obj.create(inv_val)
                operation.write({"invoice_id": invoice.id})
                for line in operation.service_ids:
                    if not line.invoice_id and not line.inv_line_id:
                        # we did the below code to update inv line id
                        # in service, other wise we can do that by
                        # creating common vals
                        invoice.write(
                            {
                                "invoice_line_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "move_id": invoice.id or False,
                                            "service_id": line.id or False,
                                            "name": line.product_id
                                                    and line.product_id.name
                                                    or "",
                                            "product_id": line.product_id
                                                          and line.product_id.id
                                                          or False,
                                            "quantity": line.qty or 0.0,
                                            "product_uom_id": line.uom_id
                                                              and line.uom_id.id
                                                              or False,
                                            "price_unit": line.list_price or 0.0,
                                        },
                                    )
                                ]
                            }
                        )
                        ser_upd_vals = {"invoice_id": invoice.id or False}
                        if invoice.invoice_line_ids:
                            inv_l_id = invoice.invoice_line_ids.search(
                                [
                                    ("service_id", "=", line.id),
                                    ("id", "in", invoice.invoice_line_ids.ids),
                                ],
                                limit=1,
                            )
                            ser_upd_vals.update(
                                {"inv_line_id": inv_l_id and inv_l_id.id or False}
                            )
                        line.write(ser_upd_vals)
                for line in operation.operation_line_ids:
                    if not line.invoice_id and not line.inv_line_id:
                        qty = 0.0
                        if line.billing_on == "volume":
                            qty = line.exp_vol or 0.0
                        elif line.billing_on == "weight":
                            qty = line.exp_gross_weight or 0.0
                        invoice.write(
                            {
                                "invoice_line_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            "move_id": invoice.id or False,
                                            "name": line.product_id
                                                    and line.product_id.name
                                                    or "",
                                            "product_id": line.product_id
                                                          and line.product_id.id
                                                          or False,
                                            "quantity": qty,
                                            "product_uom_id": line.product_id
                                                              and line.product_id.uom_id
                                                              and line.product_id.uom_id.id
                                                              or "",
                                            "price_unit": line.price or 0.0,
                                        },
                                    )
                                ]
                            }
                        )
                        ser_upd_vals = {"invoice_id": invoice.id or False}
                        if invoice.invoice_line_ids:
                            inv_l_id = invoice.invoice_line_ids.search(
                                [
                                    ("service_id", "=", line.id),
                                    ("id", "in", invoice.invoice_line_ids.ids),
                                ],
                                limit=1,
                            )
                            ser_upd_vals.update(
                                {"inv_line_id": inv_l_id and inv_l_id.id or False}
                            )
                        line.write(ser_upd_vals)

    def action_bill(self):
        """Create Bill for the freight operation."""
        bill_obj = self.env["account.move"]
        for operation in self:
            if not operation.service_ids:
                raise UserError(
                    _(
                        "L'expédition directe n'a aucune ligne de service pour la facture Veuillez d'abord ajouter la ligne de service pour générer la facture"
                        " !!!"
                    )
                )
            services = operation.mapped("routes_ids").mapped("service_ids")
            services.write({"operation_id": operation.id})
            for line in operation.service_ids:
                if not line.bill_id and not line.bill_line_id:
                    bill = bill_obj.search(
                        [
                            ("operation_id", "=", operation.id),
                            ("move_type", "=", "in_invoice"),
                            ("state", "=", "draft"),
                            ("partner_id", "=", line.vendor_id.id),
                        ],
                        limit=1,
                    )
                    if not bill:
                        bill_val = {
                            "operation_id": operation.id or False,
                            "move_type": "in_invoice",
                            "state": "draft",
                            "partner_id": line.vendor_id.id or False,
                            "invoice_date": datetime.now().strftime(DTF),
                        }
                        bill = bill_obj.create(bill_val)
                        operation.write({"bill_id": bill.id})
                    # Used write Call because of Bill Invoice is shows
                    # unbalanced issue when we direct create the line.
                    bill.write(
                        {
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "move_id": bill.id,
                                        "service_id": line.id or False,
                                        "product_id": line.product_id
                                                      and line.product_id.id
                                                      or False,
                                        "name": line.product_id
                                                and line.product_id.name
                                                or "",
                                        "quantity": line.qty or 1.0,
                                        "product_uom_id": line.uom_id
                                                          and line.uom_id.id
                                                          or False,
                                        "price_unit": line.list_price or 0.0,
                                    },
                                )
                            ]
                        }
                    )
                    ser_upd_vals = {
                        "bill_id": bill.id,
                    }
                    if bill.invoice_line_ids:
                        bill_l_id = bill.invoice_line_ids.search(
                            [
                                ("service_id", "=", line.id),
                                ("id", "in", bill.invoice_line_ids.ids),
                            ],
                            limit=1,
                        )
                        ser_upd_vals.update(
                            {"bill_line_id": bill_l_id and bill_l_id.id or False}
                        )
                    line.write(ser_upd_vals)

    def action_in_progress(self):
        """Send operation in In Progress state."""
        for operation in self:
            services = operation.mapped("routes_ids").mapped("service_ids")
            if services:
                services.write({"operation_id": operation.id})
            operation.write({"state": "in_progress"})

    def action_in_transit(self):
        """Send operation in In Transit state."""
        for operation in self:
            services = operation.mapped("routes_ids").mapped("service_ids")
            if services:
                services.write({"operation_id": operation.id})
            operation.write({"state": "in_transit"})
        vals = {
            'customer_id': self.customer_id.id,
            'folder_id': self.folder_id.id,
            'operation_id': self.id,
            'vehicle_id': False,
        }
        res = self.env['transport.entry'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'transport.entry',
            'res_id': res.id,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'target': 'current',
        }

    def action_recived(self):
        """Send operation in In Received state."""
        for operation in self:
            services = operation.mapped("routes_ids").mapped("service_ids")
            if services:
                services.write({"operation_id": operation.id})
            operation.write({"state": "recived", "act_rec_date": datetime.now().date()})
            containers = operation.operation_line_ids.mapped("container_id")
            if containers:
                containers.write({"state": "available"})

    def action_delivered(self):
        """Send Operation in Delivered State."""
        for operation in self:
            services = operation.mapped("routes_ids").mapped("service_ids")
            if services:
                services.write({"operation_id": operation.id})
            operation.write({"state": "delivered"})
            containers = operation.operation_line_ids.mapped("container_id")
            if containers:
                containers.write({"state": "available"})

    def operation_custom_clarance(self):
        """Show particular custom activity for that order."""
        self.ensure_one()
        action = self.env.ref("scs_freight.action_operation_custom").read()[0]
        for operation in self:
            customs = self.env["operation.custom"].search(
                [("operation_id", "=", operation.id)]
            )
            action["domain"] = [("id", "in", customs.ids)]
        return action


class FreightOperationLine(models.Model):
    """Freight Operation Line Model."""

    _name = "freight.operation.line"
    _description = "Order Line"
    _rec_name = "container_id"

    container_id = fields.Many2one("freight.container", string="Conteneur", required=False)
    product_id = fields.Char(string="Article/Service", required=True)
    qty = fields.Float(string="Qty", default=1.0)
    billing_on = fields.Selection(
        [("weight", "Weight"), ("volume", "Volume"), ("service", "Service")],
        string="Billing On",
        default="weight",
    )
    sale_price = fields.Float(
        compute="_compute_calculate_sale_price", string="Prix ​​de vente", store=True
    )
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    total_tax = fields.Float(string="Taxe total", compute="_compute_calculate_total_tax")
    price = fields.Float(string="Prix")
    exp_gross_weight = fields.Float(
        string="Poids brut", help="Poids prévu en kg."
    )
    exp_vol = fields.Float(string="Volume", help="Volume attendu en m3 Mesure")
    price_list_id = fields.Many2one("operation.price.list", string="Tarification")
    goods_desc = fields.Text(string="Description des biens")
    operation_id = fields.Many2one("freight.operation", string="Opération", copy=False)
    offer_id = fields.Many2one("freight.offer", string="Offre", copy=False)
    invoice_id = fields.Many2one("account.move", string="Facture")
    inv_line_id = fields.Many2one("account.move.line", string="Ligne de facture")
    name = fields.Char(string="Nom de groupe", required=False)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Domaine technique à des fins UX.")

    @api.constrains("exp_gross_weight", "exp_vol")
    def _check_weight_volume(self):
        for freight_line in self:
            if freight_line.exp_gross_weight < 0.0:
                raise UserError(_("Vous ne pouvez pas entrer de poids dans la valeur négative!!"))
            if freight_line.exp_vol < 0.0:
                raise UserError(_("Vous ne pouvez pas entrer de volume en valeur négative !!"))

    """
    @api.onchange("container_id")
    def _onchange_container_id(self):
        for freight_line in self:
            if (
                    freight_line.container_id
                    and freight_line.container_id.state == "reserve"
            ):
                raise UserError(
                    _("%s is not available!!") % freight_line.container_id.name
                )
    """

    @api.onchange("price_list_id", "billing_on")
    def _onchange_price(self):
        for line in self:
            if line.price_list_id:
                if line.billing_on == "volume":
                    line.exp_gross_weight = 0.0
                    line.price = line.price_list_id.volume_price or 0.0
                else:
                    line.exp_vol = 0.0
                    line.price = line.price_list_id.weight_price or 0.0

    @api.depends("billing_on", "price_list_id", "exp_gross_weight", "exp_vol", "price")
    def _compute_calculate_sale_price(self):
        for line in self:
            if line.billing_on == "weight":
                line.sale_price = line.exp_gross_weight * line.price * line.qty
            elif line.billing_on == "volume":
                line.sale_price = line.exp_vol * line.price * line.qty
            else:
                line.sale_price = line.price * line.qty

    def _compute_calculate_total_tax(self):

        for line in self:
            total = 0.0
            for tax in line.tax_id:
                total += (tax.amount / 100) * line.sale_price
            line.total_tax = total


class OperationRoute(models.Model):
    """Freight Operation Route."""

    _name = "operation.route"
    _description = "Itinéraires d'opérations de fret"

    route_operation = fields.Selection(
        [
            ("main_carrige", "Chariot principal"),
            ("picking", "Chargement"),
            ("oncarrige", "Sur le chariot"),
            ("precarrige", "Pré-acheminement"),
            ("delivery", "Livraison"),
        ],
        string="Opérations d'itinéraire",
    )
    date = fields.Date(string="Envoyer la date")
    recived_date = fields.Date(string="Date de réception")
    source_location = fields.Many2one("freight.port", string="Emplacement de la source")
    dest_location = fields.Many2one("freight.port", string="Lieu de destination")
    transport = fields.Selection(
        [("land", "Terrestre"), ("ocean", "Maritime"), ("air", "Aérien")], string="Transport"
    )
    operation_id = fields.Many2one("freight.operation", string="Opération")
    service_ids = fields.One2many("operation.service", "route_id", string="Services")
    cost_total = fields.Float(string="Coût", compute="_compute_cost_total", store=True)
    sale_total = fields.Float(string="Prix de vente", compute="_compute_sale_total", store=True)

    @api.constrains("date", "recived_date")
    def _check_date_received_date(self):
        """Check Send and Receive Dates."""
        for route_l in self:
            if (
                    route_l.date
                    and route_l.recived_date
                    and route_l.date > route_l.recived_date
            ):
                raise UserError(
                    _(
                        "  Routes 'Date de réception' Doit être inférieur ou égal à 'Date d'envoi' "
                        " !!"
                    )
                )

    @api.constrains("source_location", "dest_location")
    def _check_source_destination_location(self):
        """Check Source and Destination Location."""
        for route_l in self:
            if (
                    route_l.source_location
                    and route_l.dest_location
                    and route_l.source_location.id == route_l.dest_location.id
            ):
                raise UserError(
                    _("Les itinéraires 'Depuis' et 'Vers' l'emplacement  doivent être différents !!")
                )

    @api.depends("service_ids")
    def _compute_cost_total(self):
        """Compute total cost amount."""
        for route in self:
            cost_total = 0.0
            if route.service_ids:
                cost_total = sum(route.service_ids.mapped("cost_total"))
            route.cost_total = cost_total

    @api.depends("service_ids")
    def _compute_sale_total(self):
        """Compute total sale amount."""
        for route in self:
            sale_total = 0.0
            if route.service_ids:
                sale_total = sum(route.service_ids.mapped("sale_total"))
            route.sale_total = sale_total


class OperationService(models.Model):
    """Operation related Services."""

    _name = "operation.service"
    _description = "Services d'exploitation"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Service")
    operation_id = fields.Many2one("freight.operation", string="Opération")
    offer_id = fields.Many2one("freight.offer", string="Offre")
    route_id = fields.Many2one("operation.route", string="Route")
    vendor_id = fields.Many2one("res.partner", string="Fournisseur")
    invoice_id = fields.Many2one("account.move", string="Facture")
    inv_line_id = fields.Many2one("account.move.line", string="Ligne de facture")
    bill_id = fields.Many2one("account.move", string="Facture")
    bill_line_id = fields.Many2one("account.move.line", string="Ligne de mouvement")
    qty = fields.Integer(string="Quantité", default=1)
    uom_id = fields.Many2one("uom.uom", string="Unité de mesure")
    route_service = fields.Boolean(string="Est un service d'itinéraire", default=False)
    currency_id = fields.Many2one('res.currency', string='Monnaie', readonly=False,
                                  default=lambda self: self.env.ref('base.main_company').currency_id)
    rate = fields.Float(string="Cours des devises", default=1.00)
    list_price = fields.Float(string="Prix ​​de vente")
    cost_price = fields.Float(string="Coût")
    sale_total = fields.Float(
        compute="_compute_sale_total", string="Vente totale", store=True
    )
    cost_total = fields.Float(
        compute="_compute_cost_total", string="Coût total", store=True
    )
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    total_tax = fields.Float(string="Total tax", compute="_compute_calculate_total_tax")
    exp_gross_weight = fields.Float(
        string="Poids brut", help="Poids attendu en kg."
    )
    exp_vol = fields.Float(string="Volume", help="Volume attendu en m3 Mesure")

    name = fields.Char(string="Nom de groupe", required=False)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Domaine technique à des fins UX.")

    @api.constrains("qty", "list_price", "cost_price")
    def _check_qty_and_price(self):
        """Constrain to check qty and price."""
        for service in self:
            if service.qty < 0:
                raise UserError(_("Vous ne pouvez pas saisir de quantité négative pour les services!!"))
            if service.list_price < 0:
                raise UserError(
                    _("Vous ne pouvez pas entrer le prix de vente en négatif pour le service!!")
                )
            if service.cost_price < 0:
                raise UserError(
                    _("Vous ne pouvez pas entrer le prix de revient en négatif pour le service !!")
                )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Onchange to update list and cost price."""
        if self.product_id:
            self.update(
                {
                    "list_price": self.product_id.list_price or 0.0,
                    "cost_price": self.product_id.standard_price or 0.0,
                }
            )

    @api.depends("qty", "list_price")
    def _compute_sale_total(self):
        """Compute total sale amount."""
        for service in self:
            service.sale_total = service.qty * service.list_price or 0.0

    @api.depends("qty", "cost_price")
    def _compute_cost_total(self):
        """Compute total cost amount."""
        for service in self:
            service.cost_total = service.qty * service.cost_price or 0.0

    def _compute_calculate_total_tax(self):

        for service in self:
            total = 0.0
            for tax in service.tax_id:
                total += (tax.amount / 100) * service.sale_total
            service.total_tax = total


class OperationCommercialInvoice(models.Model):
    """Operation related commercial invoice."""

    _name = "operation.commercial.invoice"
    _description = "Opération factures commerciales"
    _rec_name = "product_name"

    operation_id = fields.Many2one("freight.operation", string="Opération")
    amount = fields.Float(string="Amount")
    currency_id = fields.Many2one('res.currency', string='Dévise', readonly=False,
                                  default=lambda self: self.env.ref('base.main_company').currency_id)
    rate = fields.Float(string="Cours des devises", default=1.00)
    transit_coast = fields.Float(string="Coût de transport")
    transit_currency_id = fields.Many2one('res.currency', string='Dévise de transit', readonly=False,
                                          default=lambda self: self.env.ref('base.main_company').currency_id)
    transit_rate = fields.Float(string="Cours des devises", default=1.00)
    supplier = fields.Char(string="Fournisseur")
    reference = fields.Char(string="Référence")
    product_name = fields.Char(string="Nom du produit")
