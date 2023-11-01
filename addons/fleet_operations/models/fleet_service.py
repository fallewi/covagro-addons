# See LICENSE file for full copyright and licensing details.
"""Fleet Service model."""
import time
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, ustr
from odoo.tools.float_utils import float_compare


class ServiceCategory(models.Model):
    """Service Category Model."""

    _name = 'service.category'
    _description = 'Catégorie de service de véhicule'

    name = fields.Char(string="Catégorie de services", translate=True)

    @api.constrains('name')
    def check_name(self):
        for category in self:
            if self.search_count([
                ('id', '!=', category.id),
                ('name', 'in', category.name.strip())
            ]):
                raise UserError(_('Catégorie de service avec '
                                  'Ce nom existe déjà!'))


class FleetVehicleLogServices(models.Model):
    """Fleet Vehicle Log Services Model."""

    _inherit = 'fleet.vehicle.log.services'
    _order = 'id desc'
    _rec_name = 'name'

    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_draft(self):
        if any(state not in 'draft ' for state in self.mapped('state')):
            raise UserError(_(
                'Vous ne pouvez pas supprimer le bon de travail qui '
                'à l\'état Confirmé ou Terminé !'
            ))

    @api.onchange('vehicle_id')
    def _onchange_get_vehicle_info(self):
        """Onchange Method."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.update({
                "vechical_type_id": vehicle.vechical_type_id.id or False,
                "purchaser_id": vehicle.driver_id.id or False,
                "f_brand_id": vehicle.f_brand_id.id or False,
                "vehical_division_id": vehicle.vehical_division_id.id or False
            })

    def action_create_invoice(self):
        """Invoice for Deposit Receive."""
        for service in self:
            if service.amount <= 0.0:
                raise ValidationError(
                    _("Vous ne pouvez pas créer de facture de service sans montant !!"
                      "Veuillez d'abord ajouter le montant du service !!"))

            deposit_inv_ids = self.env['account.move'].search([
                ('vehicle_service_id', '=',
                 service.id), ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['draft', 'open', 'in_payment'])
            ])
            if deposit_inv_ids:
                raise UserError(_("La facture d'acompte est déjà en attente\n"
                                  "Veuillez d'abord procéder à cette facture d'acompte"))

            if not service.purchaser_id:
                raise UserError(_("Veuillez configurer le conducteur depuis le véhicule ou dans "
                                  "une commande de service !!"))

            inv_ser_line = [(0, 0, {
                'name': ustr(service.service_type_id and
                             service.service_type_id.name) + ' - Coût des services',
                'price_unit': service.amount,
                'account_id': service.vehicle_id and
                              service.vehicle_id.income_acc_id and
                              service.vehicle_id.income_acc_id.id or False,
            })]
            for line in service.parts_ids:
                inv_line_values = {
                    'product_id': line.product_id and
                                  line.product_id.id or False,
                    'name': line.product_id and
                            line.product_id.name or '',
                    'price_unit': line.price_unit or 0.00,
                    'quantity': line.qty,
                    'account_id': service.vehicle_id and
                                  service.vehicle_id.income_acc_id and
                                  service.vehicle_id.income_acc_id.id or False
                }
                inv_ser_line.append((0, 0, inv_line_values))
            inv_values = {
                'partner_id': service.purchaser_id and
                              service.purchaser_id.id or False,
                'move_type': 'out_invoice',
                'invoice_date': service.date_open,
                'invoice_date_due': service.date_complete,
                'invoice_line_ids': inv_ser_line,
                'vehicle_service_id': service.id,
                'is_invoice_receive': True,
            }
            self.env['account.move'].create(inv_values)

    def action_return_invoice(self):
        """Invoice for Deposit Return."""
        for service in self:
            deposit_inv_ids = self.env['account.move'].search([
                ('vehicle_service_id', '=',
                 service.id), ('move_type', '=', 'out_refund'),
                ('state', 'in', ['draft', 'open', 'in_payment'])
            ])
            if deposit_inv_ids:
                raise UserError(_("La facture de retour d'acompte est déjà en attente\n"
                                  "Veuillez d'abord procéder à cette facture d'acompte"))
            invoice = self.env['account.move'].search([
                ('vehicle_service_id', '=',
                 service.id), ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ], limit=1, order='id desc')
            move_reversal = self.env['account.move.reversal'].with_context(
                active_model="account.move", active_ids=invoice.ids).create({
                'refund_method': 'refund',
            })
            move_reversal.reverse_moves()

    def action_confirm(self):
        """Action Confirm Of Button."""
        sequence = self.env['ir.sequence'].next_by_code(
            'service.order.sequence')
        context = self.env.context.copy()
        for work_order in self:
            if work_order.vehicle_id:
                if work_order.vehicle_id.state == 'write-off':
                    raise UserError(_("Vous ne pouvez pas confirmer ce bon de travail"
                                      " car le véhicule est en état de radiation !"))
                elif work_order.vehicle_id.state == 'in_progress':
                    raise UserError(
                        _("L'ordre de travail précédent n'est pas "
                          "compléter, terminer ce bon de travail d'abord que "
                          "vous pouvez confirmer cet ordre de travail !"))
                elif work_order.vehicle_id.state == 'draft' or \
                        work_order.vehicle_id.state == 'complete':
                    raise UserError(
                        _("Confirmer l'ordre de travail ne peut que"
                          "lorsque l'état du véhicule est en inspection ou autorisé !"))
                work_order.vehicle_id.write({
                    'state': 'in_progress',
                    'last_change_status_date': fields.Date.today(),
                    'work_order_close': False})
            work_order.write({'state': 'confirm', 'name': sequence,
                              'date_open':
                                  time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            pending_repair_resource_id = self.env.ref(
                'fleet_operations.continue_pending_repair_form_view'
            ).id
            context.update({'work_order_id': work_order.id,
                            'vehicle_id': work_order.vehicle_id and
                                          work_order.vehicle_id.id or False})
            if work_order.vehicle_id:
                for pending_repair in \
                        work_order.vehicle_id.pending_repair_type_ids:
                    if pending_repair.state == 'in-complete':
                        return {
                            'name': _('Types de réparation précédents'),
                            'context': context,
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'continue.pending.repair',
                            'views': [(pending_repair_resource_id, 'form')],
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                        }
        return True

    def action_done(self):
        """Action Done Of Button."""
        context = dict(self.env.context)
        odometer_increment = 0.0
        increment_obj = self.env['next.increment.number']
        next_service_day_obj = self.env['next.service.days']
        for work_order in self:
            service_inv = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', work_order.id)])
            if work_order.amount > 0 and not service_inv:
                raise ValidationError(
                    _("Le montant du service du véhicule est supérieur"
                      "Zéro. "
                      "Sans facture de service, vous ne pouvez pas effectuer le service !"
                      "Veuillez d'abord générer une facture de service !!"))
            for repair_line in work_order.repair_line_ids:
                if repair_line.complete is True:
                    continue
                elif repair_line.complete is False:
                    pending_repair_resource_id = self.env.ref(
                        "fleet_operations.pending_repair_confirm_form_view"
                    )
                    context.update({'work_order_id': work_order.id})
                    return {
                        'name': _('WO fermer avec force'),
                        'context': context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'pending.repair.confirm',
                        'views': [(pending_repair_resource_id.id, 'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }

        increment_ids = increment_obj.search([
            ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not increment_ids:
            return {
                'name': _('Prochain jour de service'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        if increment_ids:
            odometer_increment = increment_ids[0].number

        next_service_day_ids = next_service_day_obj.search([
            ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not next_service_day_ids:
            return {
                'name': _('Prochain jour de service'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        work_order_vals = {}
        for work_order in self:
            # self.env.args = cr, uid, misc.frozendict(context)
            user = self.env.user
            if work_order.odometer == 0:
                raise UserError(_("Veuillez définir l' "
                                  "Odomètre du véhicule en état de marche !"))
            odometer_increment += work_order.odometer
            next_service_date = datetime.strptime(
                str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT) + \
                                timedelta(days=next_service_day_ids[0].days)
            work_order_vals.update({
                'state': 'done',
                'next_service_odometer': odometer_increment,
                'already_closed': True,
                'closed_by': user,
                'date_close': fields.Date.today(),
                'next_service_date': next_service_date})
            work_order.write(work_order_vals)
            if work_order.vehicle_id:
                work_order.vehicle_id.write({
                    'state': 'complete',
                    'last_service_by_id': work_order.team_id and
                    work_order.team_id.id or False,
                    'last_service_date': fields.Date.today(),
                    'next_service_date': next_service_date,
                    'due_odometer': odometer_increment,
                    'due_odometer_unit': work_order.odometer_unit,
                    'last_change_status_date': fields.Date.today(),
                    'work_order_close': True})
                if work_order.already_closed:
                    for repair_line in work_order.repair_line_ids:
                        for pending_repair_line in \
                                work_order.vehicle_id.pending_repair_type_ids:
                            if repair_line.repair_type_id.id == \
                                    pending_repair_line.repair_type_id.id and \
                                    work_order.name == \
                                    pending_repair_line.name:
                                if repair_line.complete is True:
                                    pending_repair_line.unlink()
        if work_order.parts_ids:
            parts = self.env['task.line'].search([
                ('fleet_service_id', '=', work_order.id),
                ('is_deliver', '=', False)])
            for part in parts:
                part.write({'is_deliver': True})
                source_location = self.env.ref(
                    'stock.picking_type_out').default_location_src_id
                dest_location, loc = self.env['stock.warehouse']._get_partner_locations()
                move = self.env['stock.move'].create({
                    'name': 'Used in Work Order',
                    'product_id': part.product_id.id or False,
                    'location_id': source_location.id or False,
                    'location_dest_id': dest_location.id or False,
                    'product_uom': part.product_uom.id or False,
                    'product_uom_qty': part.qty or 0.0
                })
                move._action_confirm()
                move._action_assign()
                move.move_line_ids.write({'qty_done': part.qty})
                move._action_done()
        return True

    def encode_history(self):
        """Method is used to create the Encode Qty.

        History for Team Trip from WO.
        """
        wo_part_his_obj = self.env['workorder.parts.history.details']
        if self._context.get('team_trip', False):
            team_trip = self._context.get('team_trip', False)
            work_order = self._context.get('workorder', False)
            # If existing parts Updated
            wo_part_his_ids = wo_part_his_obj.search([
                ('team_id', '=', team_trip and team_trip.id or False),
                ('wo_id', '=', work_order and work_order.id or False)])
            if wo_part_his_ids:
                wo_part_his_ids.unlink()
            wo_part_dict = {}
            for part in work_order.parts_ids:
                wo_part_dict[part.product_id.id] = \
                    {'wo_en_qty': part.encoded_qty, 'qty': part.qty}
            for t_part in team_trip.allocate_part_ids:
                if t_part.product_id.id in wo_part_dict.keys():
                    new_wo_encode_qty = \
                        wo_part_dict[t_part.product_id.id]['wo_en_qty'] - \
                        wo_part_dict[t_part.product_id.id]['qty']
                    wo_part_history_vals = {
                        'team_id': team_trip.id,
                        'product_id': t_part.product_id.id,
                        'name': t_part.product_id.name,
                        'vehicle_make': t_part.product_id.vehicle_make_id.id,
                        'used_qty': wo_part_dict[t_part.product_id.id]['qty'],
                        'wo_encoded_qty':
                            wo_part_dict[t_part.product_id.id]['wo_en_qty'],
                        'new_encode_qty': new_wo_encode_qty,
                        'wo_id': work_order.id,
                        'used_date': t_part.issue_date,
                        'issued_by': self._uid or False
                    }
                    wo_part_his_obj.create(wo_part_history_vals)
                    t_part.write({'encode_qty': new_wo_encode_qty})
        return True

    def action_reopen(self):
        """Method Action Reopen."""
        for order in self:
            service_type_id = False
            try:
                service_type_id = self.env.ref('fleet.type_service_service_8')
            except ValueError:
                pass
            if not service_type_id:
                service_type_obj = self.env['fleet.service.type']
                service_type_id = service_type_obj.search([
                    ('name', '=', 'Réparation et entretien'),
                ])
                if not service_type_id:
                    service_type_id = service_type_obj.create({
                        "name": "Réparation et entretien",
                        "category":"service"
                    })
            order.write({'state': 'done'})
            new_reopen_service = order.copy()
            new_reopen_service.write({
                'source_service_id': order.id,
                'date_open': False,
                'date_close': False,
                'service_type_id': service_type_id.id,
                'amount': False,
                'team_id': False,
                'closed_by': False,
                'repair_line_ids': [(6, 0, [])],
                'parts_ids': [(6, 0, [])],
            })
            return {
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': new_reopen_service.id,
            }

    @api.depends('parts_ids')
    def _compute_get_total(self):
        for rec in self:
            rec.sub_total = sum(line.total or 0.0 for line in rec.parts_ids)

    @api.constrains('amount')
    def _check_service_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError(_("La valeur du montant du service doit être positive!"))

    def write(self, vals):
        """Method Write."""
        # if not self._context:
        #     self._context = {}
        for work_order in self:
            if work_order.vehicle_id:
                vals.update(
                    {
                        'fmp_id': work_order.vehicle_id and
                                  work_order.vehicle_id.name or "",
                        'vechical_type_id': work_order.vehicle_id and
                                            work_order.vehicle_id.vechical_type_id and
                                            work_order.vehicle_id.vechical_type_id.id or False,
                        'purchaser_id': work_order.vehicle_id and
                                        work_order.vehicle_id.driver_id and
                                        work_order.vehicle_id.driver_id.id or False,
                        'main_type': work_order.vehicle_id.main_type,
                        'f_brand_id': work_order.vehicle_id and
                                      work_order.vehicle_id.f_brand_id and
                                      work_order.vehicle_id.f_brand_id.id or False,
                        'vehical_division_id': work_order.vehicle_id and
                                               work_order.vehicle_id.vehical_division_id and
                                               work_order.vehicle_id.vehical_division_id.id or False,
                    })
        return super(FleetVehicleLogServices, self).write(vals)

    @api.model
    def _get_location(self):
        location_id = self.env['stock.location'].search([
            ('name', '=', 'Vehicle')])
        if location_id:
            return location_id.ids[0]
        return False

    @api.model
    def default_get(self, fields):
        """Method Default get."""
        vehicle_obj = self.env['fleet.vehicle']
        repair_type_obj = self.env['repair.type']
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise UserError(_("Vous ne pouvez pas créer de bon de travail "
                                      "pour un véhicule qui est déjà radié !"
                                      ))
                elif vehicle.state == 'in_progress':
                    raise UserError(
                        _("L'ordre de travail précédent n'est pas "
                          "terminé, veuillez d'abord terminer ce bon de travail que"
                          " vous pouvez créer un nouveau bon de travail !"))
                elif vehicle.state == 'rent':
                    raise UserError(_("Vous ne pouvez pas créer de bon de travail "
                                      "pour un véhicule déjà en location !"))
                elif vehicle.state == 'draft' or vehicle.state == 'complete':
                    raise UserError(_("Le nouveau bon de travail ne peut être que "
                                      "généré soit l'état du véhicule est en "
                                      "Inspection ou libération !"))
        res = super(FleetVehicleLogServices, self).default_get(fields)
        repair_type_ids = repair_type_obj.search([])
        if not repair_type_ids:
            raise UserError(_("Il n'y a pas de données pour le type de réparation, ajoutez une réparation"
                              " tapez depuis la configuration !"))
        return res

    @api.onchange('service_type_id')
    def get_repair_line(self):
        """Method get repair line."""
        repair_lines = []
        if self.service_type_id:
            for repair_type in self.service_type_id.repair_type_ids:
                repair_lines.append((0, 0, {'repair_type_id': repair_type.id}))
            self.repair_line_ids = repair_lines

    def _compute_get_total_parts_line(self):
        """Method to used to compute Parts count."""
        for work_order in self:
            work_order.total_parts_line = len([parts_line.id
                                               for parts_line in work_order.parts_ids
                                               if parts_line])

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id

    @api.constrains('date', 'date_complete')
    def check_complete_date(self):
        """Method to check complete date."""
        for vehicle in self:
            if vehicle.date and vehicle.date_complete:
                if vehicle.date_complete < vehicle.date:
                    raise ValidationError('La date estimée doit être '
                                          'Supérieur à la date d\'émission.')

    wono_id = fields.Integer(string='Demande de service No',
                             help="Prendre ce champ pour la migration des données")
    purchaser_id = fields.Many2one(
        'res.partner', string='Acheteur', related='vehicle_id.driver_id')
    name = fields.Char(string='Demande de service', size=32, readonly=True,
                       translate=True, copy=False, default="New")
    fmp_id = fields.Char(string="Identification du véhicule", size=64,
                         related='vehicle_id.name')
    wo_tax_amount = fields.Float(string='Tax', readonly=True)
    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'ELEVE'),
                                 ('low', 'FAIBLE')], default='normal',
                                string='Priorité de travail')
    date_complete = fields.Date(string='Date du service terminé ',
                                help='Date à laquelle le service est terminé')
    date_open = fields.Date(string='Date d\'ouverture',
                            help="Lorsque l'ordre de travail \
                                        confirmera que cette date sera fixée.")
    date_close = fields.Date(string='Date de clôture',
                             help="Date de clôture du bon de travail")
    closed_by = fields.Many2one('res.users', string='Fermé par')
    etic = fields.Boolean(string='Temps estimé',
                          help="Temps estimé d'achèvement",
                          default=True)
    wrk_location_id = fields.Many2one('stock.location',
                                      string='Emplacement ', readonly=True)
    wrk_attach_ids = fields.One2many('ir.attachment', 'wo_attachment_id',
                                     string='Pièces jointes')
    task_ids = fields.One2many('service.task', 'main_id',
                               string='Tâche de service')
    parts_ids = fields.One2many('task.line', 'fleet_service_id',
                                string='les pièces')
    note = fields.Text(string='Notes de journal')
    # date_child = fields.Date(related='cost_id.date', string='Cost Date',
    #                          store=True)
    sub_total = fields.Float(compute="_compute_get_total",
                             string='Montant total des pièces', store=True)
    state = fields.Selection(selection_add=[('draft', 'Nouveau'),
                                            ('confirm', 'Ouvert'), ('done', 'Fait'),
                                            ('cancel', 'Annuler')], string='Statut',
                             default='draft', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepôt')
    delivery_id = fields.Many2one('stock.picking',
                                  string='Référence de livraison', readonly=True)
    team_id = fields.Many2one('res.partner', string="Equipes")
    maintenance_team_id = fields.Many2one("stock.location", string="Equipe")
    next_service_date = fields.Date(string='Prochaine date de service')
    next_service_odometer = fields.Float(string='Prochaine valeur du compteur kilométrique',
                                         readonly=True)
    repair_line_ids = fields.One2many('service.repair.line', 'service_id',
                                      string='Lignes de réparation')
    old_parts_incoming_ship_ids = fields.One2many('stock.picking',
                                                  'work_order_old_id',
                                                  string='Vielles pièces retournées',
                                                  readonly=True)
    reopen_return_incoming_ship_ids = fields.One2many('stock.picking',
                                                      'work_order_reopen_id',
                                                      string='Rouvrir pièces retournées',
                                                      readonly=True)
    out_going_ids = fields.One2many('stock.picking', 'work_order_out_id',
                                    string='Sortant', readonly=True)
    vechical_type_id = fields.Many2one('vehicle.type', string='Type de véhicule')
    already_closed = fields.Boolean("Déjà fermé?")
    total_parts_line = fields.Integer(compute="_compute_get_total_parts_line",
                                      string='Nombre total de pièces')
    is_parts = fields.Boolean(string="Les pièces sont-elles disponibles ?")
    from_migration = fields.Boolean('De la migration')
    main_type = fields.Selection([('vehicle', 'Véhicule'),
                                  ('non-vehicle', ' Non-Véhicule')],
                                 string='Main Type')
    f_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marque')
    vehical_division_id = fields.Many2one('vehicle.divison', string='Division')
    vechical_location_id = fields.Many2one(
        related="vehicle_id.vehicle_location_id",
        string='État d\'enregistrement', store=True)
    odometer = fields.Float(compute='_compute_get_odometer',
                            inverse='_compute_set_odometer',
                            string='Dernier odomètre',
                            help='Mesure de l\'odomètre du véhicule à la \
                                moment de ce journal')
    service_amount = fields.Float(
        compute="_compute_total_service_amount", string="Montant total des services")
    source_service_id = fields.Many2one(
        'fleet.vehicle.log.services', string="Service", copy=False)
    invoice_count = fields.Integer(
        compute="_compute_count_invoice", string="Nombre de factures")
    return_inv_count = fields.Integer(
        compute="_compute_return_invoice", string="Facture de retour")
    amount_receive = fields.Boolean(
        compute="_compute_invoice_receive", string="Facture reçue")
    amount_return = fields.Boolean(string="Retour de facture")
    service_invoice_id = fields.One2many('account.move', 'vehicle_service_id',
                                         string="Facture de service")
    service_ref_invoice_id = fields.One2many('account.move',
                                             'vehicle_service_id',
                                             string="Facture de remboursement de service")
    deposit_receive = fields.Boolean(string="Dépôt reçu?")

    def _compute_invoice_receive(self):
        """Method used to check amount received."""
        for rec in self:
            invoice_rec = self.env['account.move'].search(
                [('move_type', '=', 'out_invoice'),
                 ('vehicle_service_id', '=', rec.id), ('state', 'in', [
                    'draft', 'paid']),
                 ('is_invoice_receive', '=', True)])
            if invoice_rec:
                rec.amount_receive = True
            else:
                rec.amount_receive = False

    def _compute_count_invoice(self):
        """Method used count Invoice."""
        for serv in self:
            serv.invoice_count = self.env['account.move'].search_count([
                ('move_type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', serv.id)])

    def _compute_return_invoice(self):
        """Method used to count Refund Invoice."""
        for serv in self:
            serv.return_inv_count = self.env['account.move'].search_count([
                ('move_type', '=', 'out_refund'),
                ('vehicle_service_id', '=', serv.id)])

    @api.depends('amount', 'sub_total')
    def _compute_total_service_amount(self):
        for rec in self:
            rec.service_amount = rec.sub_total + rec.amount

    def _compute_get_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
                order='value desc')
            record.odometer = vehicle_odometer.value if vehicle_odometer else 0.0

    def _compute_set_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search(
                [('vehicle_id', '=', record.vehicle_id.id)],
                limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise UserError(
                    _('Vous ne pouvez pas entrer un odomètre inférieur au précédent '
                      'odomètre %s !') % vehicle_odometer.value)
            if record.odometer:
                data = {
                    'value': record.odometer,
                    'date': fields.Date.context_today(record),
                    'vehicle_id': record.vehicle_id.id
                }
                fleet_vehicle_odometer_obj.create(data)


class WorkOrderPartsHistoryDetails(models.Model):
    """Work order Parts History Details."""

    _name = 'workorder.parts.history.details'
    _description = 'Historique des pièces du bon de travail'
    _order = 'used_date desc'

    product_id = fields.Many2one('product.product', string='Numéro de pièce',
                                 help='Le numéro de pièce')
    name = fields.Char(string='Nom de la pièce', help='Le nom de la pièce',
                       translate=True)
    vehicle_make = fields.Many2one('fleet.vehicle.model.brand',
                                   string='Marque du véhicule',
                                   help='La marque du véhicule')
    used_qty = fields.Float(string='Encoded Qty',
                            help='La quantité utilisée dans l\'ordre de travail')
    wo_encoded_qty = fields.Float(string='Qté',
                                  help='La quantité disponible à utiliser')
    new_encode_qty = fields.Float(string='Qté pour l\'encodage',
                                  help='Nouvelle quantité encodée')
    wo_id = fields.Many2one('fleet.vehicle.log.services', string='Demande de service',
                            help='Le bon de travail pour lequel la pièce a été utilisée')
    used_date = fields.Datetime(string='Date de publication')
    issued_by = fields.Many2one('res.users', string='Délivré par',
                                help='L\'utilisateur qui délivrerait les pièces')


class TripPartsHistoryDetails(models.Model):
    """Trip Parts History Details."""

    _name = 'trip.encoded.history'
    _description = 'Trip History'

    def _get_encoded_qty(self):
        res = {}
        for parts_load in self:
            res[parts_load.id] = 0.0
            total_encoded_qty = 0.0
            if parts_load.team_id and parts_load.team_id.wo_parts_ids:
                query = "select sum(used_qty) from \
                            workorder_parts_history_details where \
                            product_id=" + str(parts_load.product_id.id) + \
                        " and team_id=" + str(parts_load.team_id.id)
                self._cr.execute(query)
                result = self._cr.fetchone()
                total_encoded_qty = result and result[0] or 0.0
                parts_load.write({'encoded_qty': total_encoded_qty})
            if total_encoded_qty:
                res[parts_load.id] = total_encoded_qty
        return res

    def _get_available_qty(self):
        for rec in self:
            available_qty = rec.used_qty - rec.dummy_encoded_qty
            if available_qty < 0:
                raise UserError(_('Quantité disponible '
                                  'doit être supérieur à zéro !'))
            rec.available_qty = available_qty

    product_id = fields.Many2one('product.product', string='Numéro de pièce',
                                 help='Le numéro de pièce')
    part_name = fields.Char(string='Nom de la pièce', size=128, translate=True)
    used_qty = fields.Float(string='Qté utilisée',
                            help='La quantité utilisée')
    encoded_qty = fields.Float(string='Qté encodée',
                               help='La quantité utilisée  \
                                        dans l\'ordre de travail')
    dummy_encoded_qty = fields.Float(compute="_get_encoded_qty",
                                     string='Quantité encodée factice')
    available_qty = fields.Float(compute="_get_available_qty",
                                 string='Qté pour l\'encodage',
                                 help='La quantité disponible à utiliser')


class TripPartsHistoryDetailsTemp(models.Model):
    """Trip Parts History Details Temp."""

    _name = 'trip.encoded.history.temp'
    _description = 'Trip History Temparery'

    product_id = fields.Many2one('product.product', string='Numéro de pièce',
                                 help='Le numéro de pièce')
    used_qty = fields.Float(string='Qté utilisée',
                            help='La quantité utilisée dans le bon de travail')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string="Demande de service")


class StockPicking(models.Model):
    """Stock Picking."""

    _inherit = 'stock.picking'
    _order = 'id desc'

    work_order_out_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Demande de service")
    work_order_old_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Ancienne Demande de service")
    work_order_reopen_id = fields.Many2one('fleet.vehicle.log.services',
                                           string=" Reouverture de Demande de service")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    received_by_id = fields.Many2one('res.users', string='Received By')

    @api.model
    def create(self, vals):
        """Overridden create method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).create(vals)

    def write(self, vals):
        """Overridden write method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).write(vals)


class StockMove(models.Model):
    """Stock Move."""

    _inherit = 'stock.move'
    _order = 'id desc'

    type = fields.Many2one(related='picking_id.picking_type_id',
                           string='Type d\'expédition',
                           store=True)
    issued_received_by_id = fields.Many2one('res.users', string='Reçu par')

    @api.onchange('picking_type_id', 'location_id', 'location_dest_id')
    def onchange_move_type(self):
        """On change of move type gives source and destination location."""
        if not self.location_id and not self.location_dest_id:
            mod_obj = self.env['ir.model.data']
            location_source_id = 'stock_location_stock'
            location_dest_id = 'stock_location_stock'
            if self.picking_type_id and \
                    self.picking_type_id.code == 'incoming':
                location_source_id = 'stock_location_suppliers'
                location_dest_id = 'stock_location_stock'
            elif self.picking_type_id and \
                    self.picking_type_id.code == 'outgoing':
                location_source_id = 'stock_location_stock'
                location_dest_id = 'stock_location_customers'
            source_location = self.env.ref("stock.%s" % location_source_id)
            dest_location = self.env.ref("stock.%s" % location_dest_id)
            self.location_id = source_location and source_location[1] or False
            self.location_dest_id = dest_location and dest_location[1] or False

    @api.model
    def _default_location_source(self):
        location_id = super(StockMove, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                    [self._context['stock_warehouse_id']]):
                if rec.lot_stock_id:
                    location_id = rec.lot_stock_id.id
        return location_id

    @api.model
    def _default_location_destination(self):
        location_dest_id = super(StockMove, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                    [self._context['stock_warehouse_id']]):
                if rec.wh_output_id_stock_loc_id:
                    location_dest_id = rec.wh_output_id_stock_loc_id and \
                                       rec.wh_output_id_stock_loc_id.id or False
        return location_dest_id


class FleetWorkOrderSearch(models.TransientModel):
    """Fleet Work order search model."""

    _name = 'fleet.work.order.search'
    _description = 'Fleet Work order Search'
    _rec_name = 'state'

    state = fields.Selection([('confirm', 'Open'), ('done', 'Fermer'),
                              ('draft', 'Draft')], string='Statut')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string='Demande de service')
    fmp_id = fields.Many2one('fleet.vehicle', string='Identification du véhicule')

    def get_work_order_detail_by_advance_search(self):
        """Method to get work order detail by advance search."""
        self.ensure_one()
        return {
            'name': _('Work Order'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'fleet.vehicle.log.services',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.work_order_id.id)] if self.work_order_id else [],
            'context': self._context,
            'target': 'current',
        }


class ResUsers(models.Model):
    """Res Users Model."""

    _inherit = 'res.users'

    usersql_id = fields.Char(string='ID de l\'utilisateur',
                             help="Prendre ce champ pour la migration des données")


class IrAttachment(models.Model):
    """Ir Attachment model."""

    _inherit = 'ir.attachment'

    wo_attachment_id = fields.Many2one('fleet.vehicle.log.services')


class ServiceTask(models.Model):
    """Service Task Model."""

    _name = 'service.task'
    _description = 'Maintien de la tâche '

    main_id = fields.Many2one('fleet.vehicle.log.services',
                              string='Référence de maintenance')
    type = fields.Many2one('fleet.service.type', string='Type')
    total_type = fields.Float(string='Coût', readonly=True, default=0.0)
    product_ids = fields.One2many('task.line', 'task_id', string='Produit')
    maintenance_info = fields.Text(string='Information', translate=True)


class TaskLine(models.Model):
    """Task Line Model."""

    _name = 'task.line'
    _description = 'Task Line'

    task_id = fields.Many2one('service.task',
                              string='référence de tâche')
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services',
                                       string='Ordre de travail du véhicule')
    product_id = fields.Many2one('product.product', string='Part')
    qty_hand = fields.Float(string='Qté en main',
                            help='Quantité en main')
    qty = fields.Float(string='Utilisé', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unité')
    price_unit = fields.Float(string='Coût unitaire')
    total = fields.Float(string='Coût total')
    date_issued = fields.Datetime(string='Date d\'émission')
    issued_by = fields.Many2one('res.users', string='Délivré par',
                                default=lambda self: self._uid)
    is_deliver = fields.Boolean(string="Est-ce livré ?")

    @api.constrains('qty', 'qty_hand')
    def _check_used_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise UserError(_('Vous ne pouvez pas '
                                  'entrer la quantité utilisée comme zéro !'))

    @api.onchange('product_id', 'qty')
    def _onchange_product(self):
        for rec in self:
            if rec.product_id:
                prod = rec.product_id
                if prod.in_active_part:
                    rec.product_id = False
                    raise UserError(_('Vous ne pouvez pas sélectionner '
                                      'partie qui est inactive !'))
                rec.qty_hand = prod.qty_available or 0.0
                rec.product_uom = prod.uom_id or False
                rec.price_unit = prod.list_price or 0.0
            if rec.qty and rec.price_unit:
                rec.total = rec.qty * rec.price_unit

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        for rec in self:
            if rec.qty and rec.price_unit:
                rec.total = rec.qty * rec.price_unit

    @api.model
    def create(self, vals):
        """
        Overridden create method to add the issuer.

        of the part and the time when it was issued.
        """
        # product_obj = self.env['product.product']
        if not vals.get('issued_by', False):
            vals.update({'issued_by': self._uid})
        if not vals.get('date_issued', False):
            vals.update({'date_issued':
                             time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        if vals.get('fleet_service_id', False) and \
                vals.get('product_id', False):
            task_line_ids = self.search([
                ('fleet_service_id', '=', vals['fleet_service_id']),
                ('product_id', '=', vals['product_id'])])
            if task_line_ids:
                raise UserError(_(
                    'Vous ne pouvez pas avoir des pièces en double affectées !!!'
                ))
        return super(TaskLine, self).create(vals)

    def write(self, vals):
        """
        Overridden write method to add the issuer of the part.

        and the time when it was issued.
        """
        if vals.get('product_id', False) \
                or vals.get('qty', False) \
                or vals.get('product_uom', False) \
                or vals.get('price_unit', False) \
                or vals.get('old_part_return') in (True, False):
            vals.update({'issued_by': self._uid,
                         'date_issued':
                             time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return super(TaskLine, self).write(vals)

    @api.onchange('date_issued')
    def check_onchange_part_issue_date(self):
        """Onchange method to check the validation for part issues date."""
        context_keys = self._context.keys()
        if 'date_open' in context_keys and self.date_issued:
            date_open = self._context.get('date_open', False)
            date_open = datetime.strptime(date_open,
                                          DEFAULT_SERVER_DATE_FORMAT)
            current_date = datetime.now().date()
            #
            if not self.date_issued >= date_open and \
                    not self.date_issued <= current_date:
                self.date_issued = False
                raise UserError(
                    _('Vous ne pouvez pas entrer.'
                      'les pièces sortent soit à la date de l\'ordre de travail ouvert, soit'
                      'entre la date du bon de travail ouvert et la date actuelle !'))

    def unlink(self):
        """Overridden method to add validation before delete the history."""
        for part in self:
            if part.fleet_service_id.state == 'done':
                raise UserError(_("Vous ne pouvez pas supprimer une partie de celles déjà utilisées."))
            if part.is_deliver:
                raise UserError(_("Vous ne pouvez pas supprimer une partie de celles déjà utilisées."))
        return super(TaskLine, self).unlink()


class RepairType(models.Model):
    """Repair Type."""

    _name = 'repair.type'
    _description = 'Type de réparation de véhicule'

    name = fields.Char(string='Type de réparation', translate=True)

    @api.constrains('name')
    def check_name(self):
        for repair in self:
            if self.search_count([
                ('id', '!=', repair.id),
                ('name', 'ilike', repair.name.strip())
            ]):
                raise UserError(_('Le type de réparation portant ce nom existe déjà!'))


class ServiceRepairLine(models.Model):
    """Service Repair Line."""

    _name = 'service.repair.line'
    _description = 'Service Repair Line'

    @api.constrains('date', 'target_date')
    def check_target_completion_date(self):
        """Method to check target completion date."""
        for vehicle in self:
            if vehicle.issue_date and vehicle.target_date:
                if vehicle.target_date < vehicle.issue_date:
                    raise ValidationError(_('La date d\'achèvement cible doit être '
                                            'Supérieur à la date d\'émission.'))

    @api.constrains('target_date', 'date_complete')
    def check_etic_date(self):
        """Method to check etic date."""
        for vehicle in self:
            if vehicle.target_date and vehicle.date_complete:
                if vehicle.target_date > vehicle.date_complete:
                    raise ValidationError(
                        _('La date d\'achèvement cible des réparations doit être '
                          'moins que la date estimée.'))

    service_id = fields.Many2one('fleet.vehicle.log.services',
                                 ondelete='cascade')
    repair_type_id = fields.Many2one('repair.type', string='Type de réparation')
    categ_id = fields.Many2one('service.category', string='Catégorie')
    issue_date = fields.Date(string='Date de publication ')
    date_complete = fields.Date(related='service_id.date_complete',
                                string="Date à laquelle le service est terminé")
    target_date = fields.Date(string='Achèvement de la cible')
    complete = fields.Boolean(string='Terminé ?')


class FleetServiceType(models.Model):
    """Fleet Service Type."""

    _inherit = 'fleet.service.type'

    category = fields.Selection(selection_add=[('contract', 'Contrat'),
                                               ('service', 'Service'), ('both', 'Les deux')],
                                required=False,
                                string='Catégorie', help='Choisissez si le \
                                                service se référer aux contrats, \
                                                services de véhicule ou les deux')
    repair_type_ids = fields.Many2many('repair.type',
                                       'fleet_service_repair_type_rel',
                                       'service_type_id', 'reapir_type_id',
                                       string='Type de réparation')

    @api.constrains('name')
    def check_name(self):
        for service in self:
            if self.search_count([
                ('id', '!=', service.id),
                ('name', 'ilike', service.name.strip())
            ]):
                raise UserError(_('Le type de service portant ce nom existe déjà !'))
