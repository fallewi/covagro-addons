from odoo import _, api, fields, models
from datetime import datetime


class Offer(models.Model):
    _name = 'freight.offer'
    _rec_name = 'name'
    _description = "Freight Offers"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Reference', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    reference = fields.Char(string='Référence')
    direction = fields.Selection(
        [("import", "Importation"), ("export", "Exportation")],
        string="Direction",
        default="import",
    )
    cargo_type = fields.Selection(
        [("general", "Marchandises générales "), ("dangerous", "Cargaison dangereuse"), ("cool", "Cargaison simple")],
        string="Type de cargaison",
        default="general",
    )
    transport = fields.Selection(
        [("land", "Terre"), ("ocean", "Océan"), ("air", "Air")],
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
    incoterm_from = fields.Many2one("freight.incoterm", string="De")
    incoterm_to = fields.Many2one("freight.incoterm", string="Pour")
    consignee_id = fields.Many2one("res.partner", string="Destinataire")
    operator_id = fields.Many2one(
        "res.users", string="Opérateur", default=lambda self: self.env.user.id
    )
    currency_id = fields.Many2one('res.currency',
                                  string='Dévise',
                                  readonly=False,
                                  default=lambda self: self.env.ref('base.main_company').currency_id
                                  )
    rate = fields.Float(string="Cours des devises", default=1.00)
    loading_country_id = fields.Many2one("res.country", string="Pays de chargement")
    loading_port_id = fields.Many2one("freight.port", string="Port de chargement")
    discharg_country_id = fields.Many2one("res.country", string="Pays de décharge")
    discharg_port_id = fields.Many2one("freight.port", string="Port de décharge")
    voyage_no = fields.Char(string="Voyage No")
    vessel_id = fields.Many2one(
        "freight.vessels", string="Vessel", domain="[('transport', '=', transport)]"
    )
    airline_id = fields.Many2one("freight.airline", string="Compagnie aérienne")
    note = fields.Text(string="Notes")
    agent_id = fields.Many2one("res.partner", string="Agent")
    operation_line_ids = fields.One2many("freight.operation.line", "offer_id", string="Commande", copy=False)
    container_ids = fields.One2many("freight.offer.cargaison", "offer_id", string="Cargaison", copy=False)
    operation_service_ids = fields.One2many("operation.service", "offer_id", string="Services", copy=False)
    state = fields.Selection(
        [
            ("draft", "Nouveau"),
            ("sent", "Envoyé"),
            ("confirm", "Confirmé"),
            ("cancel", "Annulé"),
        ],
        default="draft",
        string="Statut",
    )
    exp_send_date = fields.Date(string="Date d'envoi prévue", help="Date d'envoi prévue")
    duration = fields.Char(string="Durée de transit prévue", help="Durée de transit prévue")
    exp_rec_date = fields.Date(string="Date de réception prévue", help="Date de réception prévue")

    exp_inv_payment = fields.Float(
        string="Montant de la vente", compute="_compute_expected_receivable_payment"
    )
    exp_payment_taxes = fields.Float(
        string="Taxes totales", compute="_compute_total_tax"
    )
    exp_payment_ttc = fields.Float(
        string="Total TTC", compute="_compute_total_ttc"
    )
    colis_number = fields.Integer(string="Numéro de colis", compute="_compute_colis_number")
    total_weight = fields.Float(string="Poids total", compute="_compute_colis_number")
    total_volume = fields.Float(string="Volume total", compute="_compute_colis_number")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.offer.sequence') or _('New')
        result = super(Offer, self).create(vals)
        return result

    def action_send_to_client(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('scs_freight.email_template_offer').id
        template = self.env['mail.template'].browse(template_id)
        self.state = "sent"
        ctx = {
            'default_model': 'freight.offer',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_offer_as_sent': True,
            'force_email': True
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_confirm(self):
        vals = {
            'folder_id': False,
            'direction': self.direction,
            'transport': self.transport,
            'customer_id': self.customer_id.id,
            'consignee_id': self.consignee_id.id,
            'order_date': datetime.now(),
            'company_id': 1,
            'incoterm_from': self.incoterm_from.id,
            'incoterm_to': self.incoterm_to.id,
            'loading_port_id': self.loading_port_id.id,
            'discharg_port_id': self.discharg_port_id.id,
            'exp_send_date': self.exp_send_date,
            'exp_rec_date': self.exp_rec_date,
            'operator_id': self.operator_id.id,
        }
        res = self.env['freight.operation'].create(vals)
        for rec in self.operation_service_ids:
            vals2 = {
                'product_id': rec.product_id.id,
                'vendor_id': rec.vendor_id.id,
                'qty': rec.qty,
                'operation_id': res.id,
                'invoice_id': rec.invoice_id.id,
                'inv_line_id': rec.inv_line_id.id,
                'bill_id': rec.bill_id,
                'bill_line_id': rec.bill_line_id.id,
                'currency_id': rec.currency_id.id,
                'rate': rec.rate,
                'list_price': rec.list_price,
                'cost_price': rec.cost_price,
            }

            res2 = self.env['operation.service'].create(vals2)
        self.state = 'confirm'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'freight.operation',
            'res_id': res.id,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
            'target': 'current',
        }

    def action_cancel(self):
        self.state = 'cancel'

    def action_set_to_draft(self):
        self.state = 'draft'

    def _compute_expected_receivable_payment(self):
        """Calculate the total invoice amount."""
        for operation in self:
            total = 0.0
            for line in self.operation_service_ids:
                total += line.list_price
            operation.exp_inv_payment = total

    def _compute_total_tax(self):
        """Calculate the total invoice amount."""
        for operation in self:
            total_tax = 0.0
            for line in operation.operation_service_ids:
                for tax in line.tax_id:
                    total_tax += (tax.amount / 100) * line.sale_price
            operation.exp_payment_taxes = total_tax

    def _compute_total_ttc(self):
        """Calculate the total invoice amount."""
        for operation in self:
            operation.exp_payment_ttc = operation.exp_payment_taxes + operation.exp_inv_payment

    def _compute_colis_number(self):
        for offer in self:
            offer.colis_number = len(self.container_ids)
            total_weight = 0.0
            total_volume = 0.0
            for line in self.container_ids:
                total_weight += line.weight
                total_volume += line.volume
            offer.total_weight = total_weight
            offer.total_volume = total_volume


class OfferCargaison(models.Model):
    _name = 'freight.offer.cargaison'

    offer_id = fields.Integer(string="Offre")
    operation_id = fields.Integer(string="Opération")
    container_id = fields.Many2one("freight.container", string="Conteneur", copy=False)
    long = fields.Float(string="Longueur", default=1)
    larg = fields.Float(string="Largeur", default=1)
    hot = fields.Float(string="Hot", default=1)
    qty = fields.Integer(string="Quantité", default=1)
    volume = fields.Float(string="Volume", help="Volume maximal (M3) Capacité de manutention")
    weight = fields.Float(string="Poids", help="Poids maximal (KG) Capacité de manutention")
    total_weight = fields.Float(string="Poids Total", compute="_compute_total_weight")
    taxable_weight = fields.Float(string="Poids imposable")

    @api.onchange("container_id")
    def _onchange_container_id(self):
        if self.container_id:
            self.update({
                'volume': self.container_id.volume,
                'weight': self.container_id.weight
            })

    def _compute_total_weight(self):
        for line in self:
            line.total_weight = line.weight * line.qty
