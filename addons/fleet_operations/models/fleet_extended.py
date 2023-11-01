# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """product model."""

    _inherit = 'product.product'

    in_active_part = fields.Boolean('Partie inactive ?')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Marque du véhicule')


class FleetOperations(models.Model):
    """Fleet Operations model."""

    _inherit = 'fleet.vehicle'
    _order = 'id desc'
    _rec_name = 'name'

    def copy(self, default=None):
        """Overridden copy method."""
        if not default:
            default = {}
        if self.state == 'write-off':
            raise UserError(_('Vous ne pouvez pas dupliquer cet enregistrement '
                              'parce qu\'il est déjà radié'))
        return super(FleetOperations, self).copy(default=default)

    @api.model
    def vehicle_service_reminder_send_mail(self):
        """Method to Send Next Service Reminder to vehicle driver."""
        fleet_vehicles = self.env['fleet.vehicle'].search([
            ('next_service_date', '=', fields.Date.today())])
        for vehicle in fleet_vehicles:
            if vehicle.driver_id and vehicle.driver_id.email:
                res = self.env.ref('fleet_operations.fleet_email_template')
                res.send_mail(vehicle.id, force_send=True)
        return True

    def update_history(self):
        """Method use update color engine,battery and tire history."""
        mod_obj = self.env['ir.model.data']
        wizard_view = ""
        res_model = ""
        view_name = ""
        context = self.env.context
        context = dict(context)
        if context.get('history', False):
            if context.get("history", False) == "color":
                wizard_view = "update_color_info_form_view"
                res_model = "update.color.info"
                view_name = "Update Color Info"
            elif context.get("history", False) == "engine":
                wizard_view = "update_engine_info_form_view"
                res_model = "update.engine.info"
                view_name = "Update Engine Info"
            elif context.get('history', False) == 'vin':
                wizard_view = "update_vin_info_form_view"
                res_model = "update.vin.info"
                view_name = "Update Vin Info"
            elif context.get('history', False) == 'tire':
                wizard_view = "update_tire_info_form_view"
                res_model = "update.tire.info"
                view_name = "Update Tire Info"
            elif context.get('history', False) == 'battery':
                wizard_view = "update_battery_info_form_view"
                res_model = "update.battery.info"
                view_name = "Update Battery Info"

        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'),
                                         ('name', '=', wizard_view)])
        resource_id = model_data_ids.read(['res_id'])[0]['res_id']
        context.update({'vehicle_ids': self._ids})
        # self.env.args = cr, uid, misc.frozendict(context)
        return {
            'name': view_name,
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': res_model,
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def set_released_state(self):
        """Method to set released state."""
        for vehicle in self:
            if vehicle.state == 'complete':
                vehicle.write({'state': 'released',
                               'last_change_status_date': fields.Date.today(),
                               'released_date': fields.Date.today()})
            else:
                raise UserError(_('L\'état du véhicule ne sera défini que sur libéré'
                                  's\'il est à l\'état terminé.'))
        return True

    def name_get(self):
        """
        Method will be called when you view an M2O field in a form.

        And return name whatever we want to search.
        """
        if not len(self._ids):
            return []
        res = []
        for vehicle in self:
            vehicle_unique_id = vehicle.name or ""
            vehicle_unique_id += "-"
            vehicle_unique_id += vehicle.model_id and \
                                 vehicle.model_id.name or ""
            res.append((vehicle['id'], vehicle_unique_id))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """Overwritten this method for the bypass base domain."""
        vehicle_ids = self.search(args, limit=limit)
        return vehicle_ids.name_get()

    def return_action_too_open(self):
        """
        The xml view specified in xml_id.

        For the current vehicle.
        """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']. \
                for_xml_id('fleet_operations', xml_id)
            res.update(
                context=dict(self.env.context,
                             default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    @api.constrains('tire_issuance_date', 'battery_issuance_date')
    def check_tire_issuance_date(self):
        """Method to check tire issuance date."""
        for vehicle in self:
            if vehicle.tire_issuance_date and vehicle.battery_issuance_date:
                if vehicle.battery_issuance_date < \
                        vehicle.acquisition_date and \
                        vehicle.tire_issuance_date < vehicle.acquisition_date:
                    raise ValidationError(
                        _('La date d\'émission du pneu et la date d\'émission de la batterie devraient '
                          ' Être supérieur à la date d\'enregistrement.'))
            if vehicle.tire_issuance_date and \
                    vehicle.tire_issuance_date < vehicle.acquisition_date:
                raise ValidationError(_('La date d\'émission des pneus doit être '
                                        'Supérieur à la date d\'enregistrement.'))
            if vehicle.battery_issuance_date and \
                    vehicle.battery_issuance_date < vehicle.acquisition_date:
                raise ValidationError(_('La date d\'émission de la batterie doit être '
                                        'Supérieur à la date d\'enregistrement.'))

    @api.constrains('warranty_period')
    def check_warranty_date(self):
        """Method to check warranty date."""
        for vehicle in self:
            if vehicle.warranty_period and \
                    vehicle.warranty_period < vehicle.acquisition_date:
                raise ValidationError(_('La période de garantie doit être '
                                        'Supérieur à la date d\'enregistrement.'))

    @api.constrains('driver_id')
    def check_duplicate_driver(self):
        for vehicle in self:
            if vehicle.driver_id and self.search_count([
                ('driver_id', '=', vehicle.driver_id.id),
                ('id', '!=',vehicle.id),
                ('state', '!=', 'write-off')
            ]) > 1:
                raise ValidationError(_(
                    "Le conducteur ne peut être affecté qu'à un seul véhicule !"
                ))

    @api.constrains('date_sold', 'acquisition_date')
    def check_sold_date(self):
        """Method to check sold date."""
        for vehicle in self:
            if vehicle.acquisition_date and vehicle.date_sold:
                if vehicle.date_sold < vehicle.acquisition_date:
                    raise ValidationError(_('La date de vente doit être '
                                            'Supérieur à la date d\'enregistrement.'))

    @api.constrains('date_sold', 'transfer_date')
    def check_transfer_date(self):
        """Method to check transfer date."""
        for vehicle in self:
            if vehicle.transfer_date and vehicle.date_sold:
                if vehicle.transfer_date < vehicle.date_sold:
                    raise ValidationError(_('La date de transfert doit être '
                                            'supérieure à la date de vente.'))

    @api.constrains('start_date_insurance', 'end_date_insurance')
    def check_insurance_end_date(self):
        """Method to check insurance date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.end_date_insurance:
                if vehicle.end_date_insurance < vehicle.start_date_insurance:
                    raise ValidationError(_('La date de fin de l\'assurance doit être '
                                            'supérieur à la date de début.'))

    @api.constrains('start_date_insurance', 'acquisition_date')
    def check_insurance_start_date(self):
        """Method to check insurance start date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.acquisition_date:
                if vehicle.start_date_insurance < vehicle.acquisition_date:
                    raise ValidationError(_('La date de début de l\'assurance doit être '
                                            'supérieur à la date d\'enregistrement.'))

    def _get_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise UserError(
                    _('Vous ne pouvez pas entrer un odomètre inférieur au précédent '
                      'odomètre %s !') % vehicle_odometer.value)
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.id}
                fleet_vehicle_odometer_obj.create(data)

    @api.onchange('f_brand_id')
    def _onchange_brand(self):
        if self.f_brand_id:
            self.image_128 = self.f_brand_id.image_128
        else:
            self.image_128 = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for model in self:
            if model.model_id:
                model.model_year = model.model_id.model_year or 0
                model.transmission = model.model_id.transmission or False
                model.seats = model.model_id.seats or 0
                model.doors = model.model_id.doors or 0
                model.color = model.model_id.color or ""
                model.trailer_hook = model.model_id.trailer_hook or 0
                model.fuel_type = model.model_id.default_fuel_type or False
                model.co2 = model.model_id.default_co2 or 0.0
                model.co2_standard = model.model_id.co2_standard or ""
                model.power = model.model_id.power or 0
                model.horsepower = model.model_id.horsepower or 0
                model.horsepower_tax = model.horsepower_tax or 0.0



    @api.depends('model_id', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            if record.model_id and record.model_id.brand_id:
                lic_plate = record.license_plate
                if not record.license_plate:
                    lic_plate = ''
                record.name = \
                    record.model_id.brand_id.name + '/' + \
                    record.model_id.name + '/' + lic_plate

    name = fields.Char(compute="_compute_vehicle_name", string="Vehicle-ID",
                       store=True)
    odometer_check = fields.Boolean('Changement d\'odomètre', default=True)
    fuel_qty = fields.Char(string='Qualité du carburant')
    oil_name = fields.Char(string='Nom de l\'huile')
    oil_capacity = fields.Char(string='Capacité d\'huile')
    fleet_id = fields.Integer(string='Fleet ID',
                              help="Prendre ce champ pour la migration des données")
    f_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marque')
    model_no = fields.Char(string='Modèle No', translate=True)
    license_plate = fields.Char(string='Plaque d\'immatriculation',
                                translate=True, size=32,
                                help='Numéro d\'immatriculation du véhicule.\
                                (c\'est-à-dire : numéro d\'immatriculation d\'un véhicule)')
    active = fields.Boolean(string='Active', default=True)
    dealer_id = fields.Many2one('res.partner', string='Marchand')
    mileage = fields.Integer(string='Kilométrage(K/H)')
    description = fields.Text(string='À propos du véhicule', translate=True)
    engine_size = fields.Char(string='La taille du moteur', size=16)
    cylinders = fields.Integer(string='Nombre de cylindres')
    front_tire_size = fields.Float(string='Taille du pneu avant')
    front_tire_pressure = fields.Integer(string='Pression des pneus avant')
    rear_tire_size = fields.Float(string='Taille des pneus arrière')
    rear_tire_pressure = fields.Integer(string='Pression des pneus arrière')
    last_service_date = fields.Date(string='Dernière révision', readonly=True)
    next_service_date = fields.Date(string='Service suivant', readonly=True)
    last_odometer = fields.Float(string='Odomètre du dernier entretien')
    last_odometer_unit = fields.Selection([('kilometers', 'Kilometers'),
                                           ('miles', 'Miles')],
                                          string='Unité du dernier compteur kilométrique',
                                          help='Unité du compteur kilométrique')
    due_odometer = fields.Float(string='Compteur d\'entretien suivant', readonly=True)
    due_odometer_unit = fields.Selection([('kilometers', 'Kilometers'),
                                          ('miles', 'Miles')],
                                         string='Unités d\'odomètre en raison',
                                         help='Unité du compteur kilométrique ')
    left_wiper_blade = fields.Char(string='Balai d\'essuie-glace (L)', size=8)
    right_wiper_blade = fields.Char(string='Lame d\'essuie-glace(R)', size=8)
    rr_wiper_blade = fields.Char(string='Lame d\'essuie-glace (RR)', size=8)
    vehicle_length = fields.Integer(string='Longueur(mm)')
    vehicle_width = fields.Integer(string='Largeur(mm)')
    vehicle_height = fields.Integer(string='Hauteur(mm)')
    fuel_capacity = fields.Float(string='Capacité de carburant')
    date_sold = fields.Date(string='Date de vente')
    buyer_id = fields.Many2one('res.partner', string='Acheteur')
    transfer_date = fields.Date(string='Date de transfert')
    monthly_deprication = fields.Float(string='Amortissement (mensuel)')
    resale_value = fields.Float(string='Valeur actuelle')
    salvage_value = fields.Float(string='Valeur de récupération')
    warranty_period = fields.Date(string='Garantie jusqu\'à')
    insurance_company_id = fields.Many2one('res.partner',
                                           string='Compagnie d\'assurance',
                                           domain=[('insurance', '=', True)])
    insurance_type_id = fields.Many2one('insurance.type',
                                        string='Type d\'assurance')
    policy_number = fields.Char(string='Numéro de police', size=32)
    payment = fields.Float(string='Paiement')
    start_date_insurance = fields.Date(string='Date de début')
    end_date_insurance = fields.Date(string='Date de fin')
    payment_deduction = fields.Float(string='Déduction')
    fleet_attach_ids = fields.One2many('ir.attachment', 'attachment_id',
                                       string='Accessoires de flotte')
    sale_purchase_attach_ids = fields.One2many('ir.attachment',
                                               'attachment_id_2',
                                               string='Pièces jointes du véhicules')
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer',
                            string='Dernier odomètre',
                            help='Mesure de l\'odomètre du véhicule à la \
                                moment de ce journal')
    vehical_color_id = fields.Many2one('color.color', string='Vehicle Color')
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='État d\'enregistrement')
    vehical_division_id = fields.Many2one('vehicle.divison', string='Division')
    driver_id = fields.Many2one('res.partner', 'Conducteur')
    driver_identification_no = fields.Char(string='ID du conducteur', size=64)
    driver_contact_no = fields.Char(string='Numéro de téléphone du conducteur', size=64)
    main_type = fields.Selection([('vehicle', 'Véhicule'),
                                  ('non-vehicle', 'Non-véhicule')],
                                 default='vehicle', string='Type principal')
    vechical_type_id = fields.Many2one('vehicle.type', string='Type physique')
    engine_no = fields.Char(string='Moteur No', size=64)
    multi_images = fields.Many2many('ir.attachment',
                                    'fleet_vehicle_attachment_rel',
                                    'vehicle_id',
                                    'attachment_id', string='Images multiples')
    state = fields.Selection([('inspection', 'Inspection'),
                              ('in_progress', 'En Service'),
                              ('contract', 'En Contrat'),
                              ('rent', 'On Rent'), ('complete', 'Complété'),
                              ('released', 'Libéré'),
                              ('write-off', 'Terminé')],
                             string='État du véhicule', default='inspection')
    is_id_generated = fields.Boolean(string='L\'identifiant est-il généré ?', default=False)
    increment_odometer = fields.Float(string='Compteur kilométrique à incrément suivant')
    last_change_status_date = fields.Date(string='Date du dernier changement de statut',
                                          readonly=True)
    pending_repair_type_ids = fields.One2many('pending.repair.type',
                                              'vehicle_rep_type_id',
                                              string='Types de réparation en attente',
                                              readonly=True)
    released_date = fields.Date(string='Date de parution', readonly=True)
    tire_size = fields.Char(string='La taille des pneus', size=64)
    tire_srno = fields.Char(string='Pneu S/N', size=64)
    tire_issuance_date = fields.Date(string='Date d\'émission du pneu')
    battery_size = fields.Char(string='Taille de la batterie', size=64)
    battery_srno = fields.Char(string='Numéro de série de la batterie', size=64)
    battery_issuance_date = fields.Date(string='Date d\'émission de la batterie')
    color_history_ids = fields.One2many('color.history', 'vehicle_id',
                                        string="Historique des couleurs", readonly=True)
    engine_history_ids = fields.One2many('engine.history', 'vehicle_id',
                                         string="Historique du moteur",
                                         readonly=True)
    vin_history_ids = fields.One2many('vin.history', 'vehicle_id',
                                      string="Histoire du vin", readonly=True)
    tire_history_ids = fields.One2many('tire.history', 'vehicle_id',
                                       string="Historique des pneus", readonly=True)
    battery_history_ids = fields.One2many('battery.history', 'vehicle_id',
                                          string="Battrey History",
                                          readonly=True)
    is_color_set = fields.Boolean(string='Est un jeu de couleurs?')
    is_engine_set = fields.Boolean(string='Est-ce que le moteur est défini')
    is_vin_set = fields.Boolean(string='Est-ce que Vin est défini ?')
    is_tire_size_set = fields.Boolean(string='La taille du pneu est-elle définie ?')
    is_tire_srno_set = fields.Boolean(string='Is Tire Srno set ?')
    is_tire_issue_set = fields.Boolean(string='Le problème de pneu est-il défini ?')
    is_battery_size_set = fields.Boolean(string='La taille de la batterie est-elle définie ?')
    is_battery_srno_set = fields.Boolean(string='Est-ce que la batterie Srno est définie ?')
    is_battery_issue_set = fields.Boolean(string='Le problème de batterie est-il défini ?')
	

    last_service_by_id = fields.Many2one('res.partner',
                                         string="Dernier entretien par")
    work_order_ids = fields.One2many('fleet.vehicle.log.services',
                                     'vehicle_id', string='Commande de service')
    reg_id = fields.Many2one('res.users', string='Enregistré par')
    vehicle_owner = fields.Many2one('res.users', string='Propriétaire du véhicule')
    updated_by = fields.Many2one('res.users', string='Mis à jour par')
    updated_date = fields.Date(string='Date de mise à jour')
    work_order_close = fields.Boolean(string='Work Order Close', default=True)
    fmp_id_editable = fields.Boolean(string='ID de véhicule modifiable ?')
	
	
    _sql_constraints = [('vehilce_unique', 'unique(vin_sn)',
                         'The vehicle is already exist with this vin no.!'),
                        ('fmp_unique', 'unique(name)',
                         'Le véhicule existe déjà avec cet identifiant de véhicule!')]

    income_acc_id = fields.Many2one("account.account",
                                    string="Compte de revenu")
    expence_acc_id = fields.Many2one("account.account",
                                     string="Compte de dépenses")

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        res = super(FleetOperations, self).default_get(fields)
        res['acquisition_date'] = date.today().strftime('%Y-%m-%d')
        return res

    @api.model
    def create(self, vals):
        """Create method override."""
        if not vals.get('model_id', False):
            raise UserError(_('Model is not selected for this vehicle!'))
        vals.update({'fmp_id_editable': True})
        seq = self.env['ir.sequence'].next_by_code('fleet.vehicle')
        vals.update({'name': seq})
        if self._uid:
            vals.update({'reg_id': self._uid})
        if not vals.get('acquisition_date', False):
            vals.update({'acquisition_date': fields.Date.today()})
        if not vals.get('last_change_status_date', False):
            vals.update({'last_change_status_date': fields.Date.today()})

        # checking once vin, color and engine number will be set than field
        # automatically become readonly.

        if vals.get('odometer_unit'):
            vals.update({'odometer_check': False})
        if vals.get('vin_sn', False):
            vals.update({'is_vin_set': True})
        if vals.get('vehical_color_id', False):
            vals.update({'is_color_set': True})
        if vals.get('engine_no', False):
            vals.update({'is_engine_set': True})
        if vals.get('tire_size', False):
            vals.update({'is_tire_size_set': True})
        if vals.get('tire_srno', False):
            vals.update({'is_tire_srno_set': True})
        if vals.get('tire_issuance_date', False):
            vals.update({'is_tire_issue_set': True})

        if vals.get('battery_size', False):
            vals.update({'is_battery_size_set': True})
        if vals.get('battery_srno', False):
            vals.update({'is_battery_srno_set': True})
        if vals.get('battery_issuance_date', False):
            vals.update({'is_battery_issue_set': True})

        return super(FleetOperations, self).create(vals)

    def write(self, vals):
        """
        Function write an entry in the open chatter whenever.

        we change important information.

        on the vehicle like the model, the drive, the state of the vehicle.

        or its license plate.
        """
        vals.update({'fmp_id_editable': True})
        if self._uid:
            vals.update({'updated_by': self.env.user.id})
            vals.update({'updated_date': fields.Date.today()})

        if vals.get('tire_size', False):
            vals.update({'is_tire_size_set': True})
        if vals.get('tire_srno', False):
            vals.update({'is_tire_srno_set': True})
        if vals.get('tire_issuance_date', False):
            vals.update({'is_tire_issue_set': True})

        if vals.get('battery_size', False):
            vals.update({'is_battery_size_set': True})
        if vals.get('battery_srno', False):
            vals.update({'is_battery_srno_set': True})
        if vals.get('battery_issuance_date', False):
            vals.update({'is_battery_issue_set': True})

        return super(FleetOperations, self).write(vals)

    @api.onchange('driver_id')
    def get_driver_id_no(self):
        """Method to get driver id no."""
        if self.driver_id:
            driver = self.driver_id
            self.driver_identification_no = driver.d_id or ''
            self.driver_contact_no = driver.mobile
        else:
            self.driver_identification_no = ''
            self.driver_contact_no = ''


class ColorHistory(models.Model):
    """Model color history."""

    _name = 'color.history'
    _description = 'Historique des couleurs pour le véhicule'


    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    previous_color_id = fields.Many2one('color.color', string="Couleur précédente")
    current_color_id = fields.Many2one('color.color', string="Nouvelle couleur")
    changed_date = fields.Date(string='Date de modification')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Ordre de travail')
								   
class EngineHistory(models.Model):
    """Model Engine History."""

    _name = 'engine.history'
    _description = 'Historique du moteur du véhicule'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    previous_engine_no = fields.Char(string='Numéro de moteur précédent')
    new_engine_no = fields.Char(string='Nouveau moteur No')
    changed_date = fields.Date(string='Changer la date')
    note = fields.Text('Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Ordre de travail')

class VinHistory(models.Model):
    """Model Vin History."""

    _name = 'vin.history'
    _description = 'Histoire du VIN'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    previous_vin_no = fields.Char(string='Numéro de vin précédent', translate=True)
    new_vin_no = fields.Char(string='Nouveau Numéro de vin', translate=True)
    changed_date = fields.Date(string='Date de changement')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')


class TireHistory(models.Model):
    """Model Tire History."""

    _name = 'tire.history'
    _description = 'Historique des pneus du véhicule'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    previous_tire_size = fields.Char(string='Taille de pneu précédente', size=124,
                                     translate=True)
    new_tire_size = fields.Char(string="Nouvelle taille de pneu", size=124,
                                translate=True)
    previous_tire_sn = fields.Char(string='Série de pneus précédente', size=124,
                                   translate=True)
    new_tire_sn = fields.Char(string="Nouvelle série de pneus", size=124)
    previous_tire_issue_date = fields.Date(
        string='Date d\'émission du pneu précédent')
    new_tire_issue_date = fields.Date(string='Date d\'émission du nouveau pneu')
    changed_date = fields.Date(string='Date de changement')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')


class BatteryHistory(models.Model):
    """Model Battery History."""

    _name = 'battery.history'
    _description = 'Historique de la batterie du véhicule'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    previous_battery_size = fields.Char(string='Taille de la batterie précédente',
                                        size=124)
    new_battery_size = fields.Char(string="Nouvelle taille de batterie", size=124)
    previous_battery_sn = fields.Char(string='Numéro de série de la batterie précédente',
                                      size=124)
    new_battery_sn = fields.Char(string="Nouvelle série de batterie", size=124)
    previous_battery_issue_date = fields.Date(
        string='Date d\'émission de la batterie précédente')
    new_battery_issue_date = fields.Date(string='Date d\'émission de la nouvelle batterie')
    changed_date = fields.Date(string='Date de changement')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')


class PendingRepairType(models.Model):
    """Model Pending Repair Type."""

    _name = 'pending.repair.type'
    _description = 'Type de réparation en attente'

    vehicle_rep_type_id = fields.Many2one('fleet.vehicle', string="Véhicule")
    repair_type_id = fields.Many2one('repair.type', string="Type de réparation")
    name = fields.Char(string='Demande de service #', translate=True)
    categ_id = fields.Many2one("service.category", string="Catégorie")
    issue_date = fields.Date(string="Date d'émission")
    state = fields.Selection([('complete', 'Terminé'),
                              ('in-complete', 'En Attente')], string="Statut")
    user_id = fields.Many2one('res.users', string="Par")


class VehicleDivision(models.Model):
    """Model Vehicle Division."""

    _name = 'vehicle.divison'
    _description = 'Division des véhicules'

    code = fields.Char(string='Code', size=3, translate=True)
    name = fields.Char(string='Nom', required=True, translate=True)

    _sql_constraints = [('vehicle.divison_uniq', 'unique(name)',
                         'Cette division existe déjà!')]


class VehicleType(models.Model):
    """Model Vehicle Type."""

    _name = 'vehicle.type'
    _description = 'Vehicle Type'

    code = fields.Char(string='Code', translate=True)
    name = fields.Char(string='Nom', required=True,
                       translate=True)

    @api.constrains('name')
    def _check_unique_vehicle_type(self):
        for vehicle_type in self:
            if self.search_count([
                ('id', '!=', vehicle_type.id),
                ('name', 'ilike', vehicle_type.name.strip())
            ]):
                raise UserError(_('Le type de véhicule portant ce nom existe déjà !'))


class VehicleLocation(models.Model):
    """Model Vehicle Location."""

    _name = 'vehicle.location'
    _description = 'Emplacement du véhicule'

    code = fields.Char(string='Code', size=3, translate=True)
    name = fields.Char(string='Nom', size=64, required=True,
                       translate=True)


class VehicleDepartment(models.Model):
    """Model Vehicle Department."""

    _name = 'vehicle.department'
    _description = 'Département des véhicules'

    code = fields.Char(string='Code', size=10, translate=True)
    name = fields.Char(string='Nom', size=132, required=True, translate=True)


class ColorColor(models.Model):
    """Model Color."""

    _name = 'color.color'
    _description = 'Colors'

    code = fields.Char(string='Code', translate=True)
    name = fields.Char(string='Nom', required=True, translate=True)

    @api.constrains('name')
    def check_color(self):
        """Method to check duplicate value."""
        for rec in self:
            if self.env['color.color'].search_count([
                ('name', 'ilike', rec.name.strip()),
                ('id', '!=', rec.id)
            ]):
                raise ValidationError(_("Cette couleur existe déjà"))


class IrAttachment(models.Model):
    """Model Ir Attachment."""

    _inherit = 'ir.attachment'

    attachment_id = fields.Many2one('fleet.vehicle')
    attachment_id_2 = fields.Many2one('fleet.vehicle')


class FleetWittenOff(models.Model):
    """Model Fleet Witten Off."""

    _name = 'fleet.wittenoff'
    _description = 'Wittenoff Vehicles'
    _order = 'id desc'
    _rec_name = 'vehicle_id'

    name = fields.Char(string="Name")
    fleet_id = fields.Integer(string='ID de flotte',
                              help="Prendre ce champ pour la migration des données")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule',
                                 required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env['res.company']._default_currency_id(),
        string='Currency',
        help="L'autre devise facultative s'il s'agit d'une entrée multidevise."
    )
    vehicle_fmp_id = fields.Char(string='Véhicule ID', size=64)
    vin_no = fields.Char(string='VIN No', size=64, translate=True)
    color_id = fields.Many2one('color.color', string='Color')
    vehicle_plate = fields.Char(string='Plaque de véhicule No.', translate=True)
    report_date = fields.Date(string='Date du compte rendu')
    odometer = fields.Float(string='Odomètre')
    cost_esitmation = fields.Float(string='Estimation du coût')
    note_for_cause_damage = fields.Text(string='Cause du dommage',
                                        translate=True)
    note = fields.Text(string='Note', translate=True)
    cancel_note = fields.Text(string='Annuler la Remarque', translate=True)
    multi_images = fields.Many2many('ir.attachment',
                                    'fleet_written_off_attachment_rel',
                                    'writeoff_id',
                                    'attachment_id', string='Images multiples')
    damage_type_ids = fields.Many2many('damage.types',
                                       'fleet_wittenoff_damage_types_rel',
                                       'write_off_id', 'damage_id',
                                       string="Type de dégâts")
    repair_type_ids = fields.Many2many('repair.type',
                                       'fleet_wittenoff_repair_types_rel',
                                       'write_off_id', 'repair_id',
                                       string="Type de réparation")
    location_id = fields.Many2one('vehicle.location', string='Emplacement')
    driver_id = fields.Many2one('res.partner', string='Driver')
    write_off_type = fields.Selection([
        ('general_accident', 'Accident général'),
        ('insurgent_attack', 'Attaque des insurgés')],
        string='Write-off Type', default='general_accident')
    contact_no = fields.Char(string='Numéro de téléphone du conducteur')
    odometer_unit = fields.Selection([('kilometers', 'Kilomètres'),
                                      ('miles', 'Miles')],
                                     string='Unité d\'odomètre',
                                     help='Unité du compteur kilométrique')
    province_id = fields.Many2one('res.country.state', 'État d\'enregistrement')
    division_id = fields.Many2one('vehicle.divison', 'Division')
    state = fields.Selection([('draft', 'Brouillon'), ('confirm', 'Confirmé'),
                              ('cancel', 'Annulé')],
                             string='State', default='draft')
    date_cancel = fields.Date(string='Date d\'annulation')
    cancel_by_id = fields.Many2one('res.users', string="Annulé par")

    @api.constrains('cost_esitmation')
    def check_estimation_cost(self):
        for cost in self:
            if cost.cost_esitmation < 0:
                raise ValidationError(_(
                    "Les frais de réparation ne doivent pas être négatifs!"
                ))

    def write(self, vals):
        """Override write method and update values."""
        for fleet_witten in self:
            if fleet_witten.vehicle_id:
                vals.update(
                    {'vin_no': fleet_witten.vehicle_id and
                               fleet_witten.vehicle_id.vin_sn or "",
                     'vehicle_fmp_id': fleet_witten.vehicle_id and
                                       fleet_witten.vehicle_id.name or "",
                     'color_id': fleet_witten.vehicle_id and
                                 fleet_witten.vehicle_id.vehical_color_id and
                                 fleet_witten.vehicle_id.vehical_color_id.id or False,
                     'vehicle_plate': fleet_witten.vehicle_id and
                                      fleet_witten.vehicle_id.license_plate or "",
                     'province_id': fleet_witten.vehicle_id and
                                    fleet_witten.vehicle_id.vehicle_location_id and
                                    fleet_witten.vehicle_id.vehicle_location_id.id or False,
                     'division_id': fleet_witten.vehicle_id and
                                    fleet_witten.vehicle_id.vehical_division_id and
                                    fleet_witten.vehicle_id.vehical_division_id.id or False,
                     'driver_id': fleet_witten.vehicle_id and
                                  fleet_witten.vehicle_id.driver_id and
                                  fleet_witten.vehicle_id.driver_id.id or False,
                     'contact_no': fleet_witten.vehicle_id and
                                   fleet_witten.vehicle_id.driver_id and
                                   fleet_witten.vehicle_id.driver_id.mobile or "",
                     'odometer': fleet_witten.vehicle_id and
                                 fleet_witten.vehicle_id.odometer or 0.0,
                     'odometer_unit': fleet_witten.vehicle_id and
                                      fleet_witten.vehicle_id.odometer_unit or False,
                     })
        return super(FleetWittenOff, self).write(vals)

    @api.model
    def default_get(self, fields):
        """Default get method update in state changing record."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(FleetWittenOff, self).default_get(fields)
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise UserError(_("This vehicle is already in "
                                      "write-off state!"))
                elif vehicle.state == 'in_progress' or \
                        vehicle.state == 'complete':
                    raise UserError(_("Vous ne pouvez pas radier ce véhicule "
                                      "qui est à l'état En cours ou Terminé!"
                                      ))
                # elif vehicle.state == 'inspection':
                #     raise UserError(_("You can\'t write-off this "
                #                       "vehicle which is in Inspection"))
                elif vehicle.state == 'rent':
                    raise UserError(_("Vous ne pouvez pas annuler cela"
                                      "véhicule qui est en location."))
                res.update({'contact_no': vehicle.driver_contact_no or ''})
        return res

    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        """Method to get vehicle information."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.province_id = vehicle.vehicle_location_id and \
                               vehicle.vehicle_location_id.id or False
            self.driver_id = \
                vehicle.driver_id and vehicle.driver_id.id or False
            self.contact_no = vehicle.driver_contact_no or ''
            self.vin_no = vehicle.vin_sn or ''
            self.vehicle_fmp_id = vehicle.name or ''
            self.color_id = vehicle.vehical_color_id and \
                            vehicle.vehical_color_id.id or False
            self.vehicle_plate = vehicle.license_plate or ''
            self.odometer = vehicle.odometer or 0.0
            self.odometer_unit = vehicle.odometer_unit or False
            self.division_id = vehicle.vehical_division_id and \
                               vehicle.vehical_division_id.id or False

    def cancel_writeoff(self):
        """Button method in cancel state in the write off."""
        return {
            'name': 'Annuler le formulaire d\'annulation',
            'res_model': 'writeoff.cancel.reason',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    def confirm_writeoff(self):
        """Confirm button method in the writeoff state."""
        for wr_off in self:
            if wr_off.vehicle_id:
                wr_off.vehicle_id.write(
                    {'state': 'write-off',
                     'last_change_status_date': fields.Date.today(),
                     })
            wr_off.write({
                'state': 'confirm',
                'name': self.env['ir.sequence'].
                    next_by_code('vehicle.writeoff.sequnce'),
            })

    def action_set_to_draft(self):
        """Button method to set state in draft."""
        for wr_off in self:
            wr_off.write({
                'state': 'draft',
            })

    def get_usd_currency(self):
        """Method to get usd currency."""
        currency_obj = self.env['res.currency']
        usd_ids = currency_obj.search([('name', '=', 'XOF')])
        if not usd_ids:
            raise UserError(
                _("Veuillez vérifier que la devise XOF ne figure pas dans votre liste!"))
        usd = usd_ids and usd_ids[0] or False
        return usd


class FleetVehicleModel(models.Model):
    """Model Fleet Vehicle."""

    _inherit = 'fleet.vehicle.model'
    _rec_name = 'name'

    name = fields.Char(string='Nom du modèle',
                       required=True, translate=True)
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Marque',
                               required=True, help='Marque du véhicule')

    image_128 = fields.Image(string="Image", readonly=False)

    _sql_constraints = [('model_brand_name_uniq', 'unique(name,brand_id)',
                         'Le modèle avec ce nom de marque et cette marque '
                         'existe déjà!')]


class FleetVehicleModelBrand(models.Model):
    """Model Fleet Vehicle Model Brand."""

    _inherit = 'fleet.vehicle.model.brand'

    name = fields.Char(string='Marque', size=64, required=True,
                       translate=True)

    @api.constrains('name')
    def _check_duplicate_model_brand(self):
        """Method to check duplicate damage type."""
        for model in self:
            if self.search_count([
                ('name', 'ilike', model.name.strip()),
                ('id', '!=', model.id)
            ]):
                raise ValidationError(_("La marque modèle portant ce nom existe déjà!"))


class FleetVehicleAdvanceSearch(models.TransientModel):
    """Model fleet vehicle advance search."""

    _name = 'fleet.vehicle.advance.search'
    _description = 'Recherche avancée de véhicule'
    _rec_name = 'fmp_id'

    fmp_id = fields.Many2one('fleet.vehicle', string="Vehicle ID")
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='Province')
    state = fields.Selection([('inspection', 'Inspection'),
                              ('in_progress', 'En Progès'),
                              ('complete', 'Terminé'),
                              ('released', 'Libéré'),
                              ('write-off', 'Radié')], string='Statut')
    vehical_color_id = fields.Many2one('color.color', string='Couleur')
    vin_no = fields.Char(string='NIN No', size=64)
    engine_no = fields.Char(string='Moteur No', size=64)
    last_service_date = fields.Date(string='Dernière révision')
    last_service_date_to = fields.Date(string='Dernier service à')
    next_service_date = fields.Date(string='Service suivant à partir de')
    next_service_date_to = fields.Date(string='Service suivant à')
    acquisition_date = fields.Date(string="Inscription à partir de")
    acquisition_date_to = fields.Date(string="Inscription à")
    release_date_from = fields.Date(string='Libéré de')
    release_date_to = fields.Date(string='Publié à')
    driver_identification_no = fields.Char(string='ID du conducteur', size=64)
    vechical_type_id = fields.Many2one('vehicle.type', string='Type de véhicule')
    division_id = fields.Many2one('vehicle.divison', string="Division")
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Marque")
    model_id = fields.Many2one("fleet.vehicle.model", string="Modèle")

    # @api.constrains('acquisition_date', 'acquisition_date_to')
    # def check_registration_date(self):
    #     """Method to check registration date."""
    #     for vehicle in self:
    #         if vehicle.acquisition_date_to and \
    #                 vehicle.acquisition_date_to < vehicle.acquisition_date:
    #             raise ValidationError('Registration To Date Should Be '
    #                                   'Greater Than Registration From Date.')
    #
    # @api.constrains('last_service_date', 'last_service_date_to')
    # def check_last_service_date(self):
    #     """Method to check last service date."""
    #     for vehicle in self:
    #         if vehicle.last_service_date_to and \
    #                 vehicle.last_service_date_to < vehicle.last_service_date:
    #             raise ValidationError('Last Service To Date Should Be '
    #                                   'Greater Than Last Service From Date.')
    #
    # @api.constrains('next_service_date', 'next_service_date_to')
    # def check_next_service_date(self):
    #     """Method to check next service date."""
    #     for vehicle in self:
    #         if vehicle.next_service_date_to and \
    #                 vehicle.next_service_date_to < vehicle.next_service_date:
    #             raise ValidationError('Next Service To Date Should Be '
    #                                   'Greater Than Next Service From Date.')
    #
    # @api.constrains('release_date_from', 'release_date_to')
    # def check_released_date(self):
    #     """Method to check released date."""
    #     for vehicle in self:
    #         if vehicle.release_date_to and \
    #                 vehicle.release_date_to < vehicle.release_date_from:
    #             raise ValidationError('Released To Date Should Be '
    #                                   'Greater Than Released From Date.')
    #
    # def get_vehicle_detail_by_advance_search(self):
    #     """Method to get vehicle detail by advance search."""
    #     domain = []
    #     vehicle_obj = self.env['fleet.vehicle']
    #     vehicle_ids = []
    #     for vehicle in self:
    #         if vehicle.make_id:
    #             vehicle_ids = vehicle_obj.search([
    #                 ('f_brand_id', '=', vehicle.make_id.id)])
    #         if vehicle.model_id:
    #             vehicle_ids = vehicle_obj.search([
    #                 ('model_id', '=', vehicle.model_id.id)])
    #
    #         if vehicle.state:
    #             domain += ('state', '=', vehicle.state),
    #         if vehicle.fmp_id:
    #             domain += ('id', '=', vehicle.fmp_id.id),
    #         if vehicle.vehicle_location_id:
    #             domain += [('vehicle_location_id', '=',
    #                         vehicle.vehicle_location_id.id)]
    #         if vehicle.division_id:
    #             domain += [('vehical_division_id', '=',
    #                         vehicle.division_id.id)]
    #         if vehicle.vechical_type_id:
    #             domain += [('vechical_type_id', '=',
    #                         vehicle.vechical_type_id.id)]
    #         if vehicle.vehical_color_id:
    #             domain += [('vehical_color_id', '=',
    #                         vehicle.vehical_color_id.id)]
    #         if vehicle.vin_no:
    #             domain += [('vin_sn', '=', vehicle.vin_no)]
    #         if vehicle.engine_no:
    #             domain += [('engine_no', '=', vehicle.engine_no)]
    #         if vehicle.driver_identification_no:
    #             domain += [('driver_identification_no', '=',
    #                         vehicle.driver_identification_no)]
    #         if vehicle.last_service_date and vehicle.last_service_date_to:
    #             domain += [('last_service_date', '>=',
    #                         vehicle.last_service_date)]
    #             domain += [('last_service_date', '<=',
    #                         vehicle.last_service_date_to)]
    #         elif vehicle.last_service_date:
    #             domain += [('last_service_date', '=',
    #                         vehicle.last_service_date)]
    #         if vehicle.next_service_date and vehicle.next_service_date_to:
    #             domain += [('next_service_date', '>=',
    #                         vehicle.next_service_date)]
    #             domain += [('next_service_date', '<=',
    #                         vehicle.next_service_date_to)]
    #         elif vehicle.next_service_date:
    #             domain += [('next_service_date', '=',
    #                         vehicle.next_service_date)]
    #         if vehicle.acquisition_date and vehicle.acquisition_date_to:
    #             domain += [('acquisition_date', '>=',
    #                         vehicle.acquisition_date)]
    #             domain += [('acquisition_date', '<=',
    #                         vehicle.acquisition_date_to)]
    #         elif vehicle.acquisition_date:
    #             domain += [('acquisition_date', '=', vehicle.acquisition_date)]
    #         if vehicle.release_date_from and vehicle.release_date_to:
    #             domain += [('released_date', '>=', vehicle.release_date_from)]
    #             domain += [('released_date', '<=', vehicle.release_date_to)]
    #         elif vehicle.release_date_from:
    #             domain += [('released_date', '=', vehicle.release_date_from)]
    #         if vehicle.make_id or vehicle.model_id:
    #             vehicle_ids = sorted(set(vehicle_ids.ids))
    #             domain += [('id', 'in', vehicle_ids)]
    #         return {
    #             'name': _('Vehicle Registration'),
    #             'view_type': 'form',
    #             "view_mode": 'tree,form',
    #             'res_model': 'fleet.vehicle',
    #             'type': 'ir.actions.act_window',
    #             'nodestroy': True,
    #             'domain': domain,
    #             'context': self._context,
    #             'target': 'current',
    #         }
    #     return True


class VehicleUniqueSequence(models.Model):
    """Model Vehicle Unique Sequence."""

    _name = 'vehicle.unique.sequence'
    _description = 'Vehicle Unique Sequence'

    name = fields.Char(string='Nom', size=124, translate=True)
    vehicle_location_id = fields.Many2one('res.country.state',
                                          string='Emplacement ')
    make_id = fields.Many2one('fleet.vehicle.model.brand', string='Marque')
    sequence_id = fields.Many2one('ir.sequence', string='Séquence')

    _sql_constraints = [
        ('location_make_name_uniq',
         'unique (vehicle_location_id,make_id,sequence_id)',
         'Emplacement, la Marque et la Séquence doivent tous être \
                unique pour séquence unique !')
    ]


class NextIncrementNumber(models.Model):
    """Model Next Increment NUmber."""

    _name = 'next.increment.number'
    _description = 'Numéro d\'incrément suivant'

    name = fields.Char(string='Nom', size=64, translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Id du Véhicle')
    number = fields.Float(string='Incrément du compteur kilométrique')

    @api.constrains('number')
    def check_odometer_number(self):
        for rec in self:
            if rec.number < 0.0:
                raise ValidationError(_(
                    'Vous ne pouvez pas ajouter de valeur négative'
                    'pour le numéro d\'odomètre du véhicule!'
                ))

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        """Method to check last service date."""
        next_number = self.env['next.increment.number']
        for increment in self:
            if next_number.search_count([
                ('vehicle_id', '=', increment.vehicle_id.id),
                ('id', '!=', increment.id)
            ]):
                raise ValidationError(
                    _('Vous ne pouvez pas ajouter plus d\'un odomètre '
                      'configuration d\'incrément pour le même véhicule.!!!'))


class NextServiceDays(models.Model):
    """Model Next Service Days."""

    _name = 'next.service.days'
    _description = 'Prochains jours de service'

    name = fields.Char(string='Nom', translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Id du Véhicule ')
    days = fields.Integer(string='Jours')

    @api.constrains('days')
    def check_service_days(self):
        for rec in self:
            if rec.days < 0:
                raise ValidationError(_(
                    'Vous ne pouvez pas ajouter de valeur négative'
                    'prochains jours de service !'
                ))

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        """Method to check last service date."""
        for service in self:
            if self.search_count([
                ('vehicle_id', '=', service.vehicle_id.id),
                ('id', '!=', service.id)
            ]):
                raise ValidationError(
                    _('Vous ne pouvez pas ajouter plus d\'un suivant '
                      'Configuration des jours de service pour le même véhicule.!!!'))


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = 'damage.types'
    _description = 'Types de dégâts'

    name = fields.Char(string='Nom', translate=True)
    code = fields.Char(string='Code')

    @api.constrains('name', 'code')
    def _check_duplicate_damage_type(self):
        """Method to check duplicate damage type."""
        for damage in self:
            if self.search_count([
                ('name', 'ilike', damage.name.strip()),
                ('code', 'ilike', damage.code.strip()),
                ('id', '!=', damage.id)
            ]):
                raise ValidationError(_("Vous ne pouvez pas ajouter de doublon"
                                        " types de dégâts!"))


# TODO
# class VehicleFuelLog(models.Model):
#     """Model Vehicle Fuel Log."""

#     _inherit = 'fleet.vehicle.log.fuel'

#     _order = 'id desc'

#     def _get_odometer(self):
#         fleetvehicalodometer = self.env['fleet.vehicle.odometer']
#         for record in self:
#             vehicle_odometer = fleetvehicalodometer.search([
#                 ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
#                 order='value desc')
#             if vehicle_odometer:
#                 record.odometer = vehicle_odometer.value
#             else:
#                 record.odometer = 0

#     def _set_odometer(self):
#         fleetvehicalodometer = self.env['fleet.vehicle.odometer']
#         for record in self:
#             vehicle_odometer = fleetvehicalodometer.search(
#                 [('vehicle_id', '=', record.vehicle_id.id)],
#                 limit=1, order='value desc')
#             if record.odometer < vehicle_odometer.value:
#                 raise Warning(_('You can\'t enter odometer less than previous'
#                               'odometer %s !') % (vehicle_odometer.value))
#             if record.odometer:
#                 date = fields.Date.context_today(record)
#                 data = {'value': record.odometer, 'date': date,
#                         'vehicle_id': record.vehicle_id.id}
#                 fleetvehicalodometer.create(data)

#     @api.onchange('vehicle_id')
#     def _onchange_vehicle(self):
#         if not self.vehicle_id:
#             return {}
#         if self.vehicle_id:
#             self.odometer = self.vehicle_id.odometer
#             self.odometer_unit = self.vehicle_id.odometer_unit
#             self.purchaser_id = self.vehicle_id.driver_id.id

#     odometer = fields.Float(
#         compute='_get_odometer',
#         inverse='_set_odometer',
#         string='Last Odometer',
#         help='Odometer measure of the vehicle at the moment of this log')
#     odometer_unit = fields.Selection(
#         related='vehicle_id.odometer_unit',
#         help='Unit of the odometer ', store=True)
#     make = fields.Many2one(related='vehicle_id.f_brand_id',
#                            string='Marque', store=True)
#     model = fields.Many2one(related='vehicle_id.model_id',
#                             string='Model', store=True)
#     current_fuel = fields.Float(string='Current Fuel', size=64)
#     fuel_type = fields.Selection(related='vehicle_id.fuel_type',
#                                  store=True,
#                                  help='Fuel Used by the vehicle')

#     @api.model
#     def default_get(self, fields):
#         """Vehicle fuel log default get the records."""
#         res = super(VehicleFuelLog, self).default_get(fields)
#         fleet_obj = self.env['fleet.vehicle']
#         if self._context:
#             ctx_keys = self._context.keys()
#             if 'active_model' in ctx_keys:
#                 if 'active_id' in ctx_keys:
#                     vehicle_id = self.env[self._context[
#                         'active_model']].browse(
#                         self._context['active_id'])
#                     if vehicle_id.state != 'write-off':
#                         res.update({'vehicle_id': self._context['active_id']})
#                     else:
#                         res['vehicle_id'] = False
#             if 'vehicle_id' in ctx_keys:
#                 vehicle_id = fleet_obj.browse(self._context['vehicle_id'])
#                 if vehicle_id.state != 'write-off':
#                     res.update({'vehicle_id': self._context['vehicle_id']})
#         return res

#     def copy(self, default=None):
#         """
#         Method copy for can not duplicate records.

#         In the vehicle fuel log.
#         """
#         if not default:
#             default = {}
#         raise Warning(_('You can\'t duplicate record!'))

# TODO
# class FleetVehicleCost(models.Model):
#     """Model Fleet Vehicle Cost."""

#     _inherit = 'fleet.vehicle.cost'

#     @api.model
#     def default_get(self, fields):
#         """Default get method is set vehilce id."""
#         res = super(FleetVehicleCost, self).default_get(fields)
#         fleet_obj = self.env['fleet.vehicle']
#         if self._context.get('active_id', False):
#             vehicle_id = fleet_obj.browse(self._context['active_id'])
#             if vehicle_id.state == 'write-off':
#                 res['vehicle_id'] = False
#         return res


class FleetVehicleOdometer(models.Model):
    """Model Fleet Vehicle Odometer."""

    _inherit = 'fleet.vehicle.odometer'
    _description = 'Journal d\'odomètre pour un véhicule'
    _order = 'date desc'

    def _compute_vehicle_log_name_get_fnc(self):
        for record in self:
            name = record.vehicle_id and record.vehicle_id.name or False
            if record.date:
                if not name:
                    name = "New/" + str(record.date)
                name = name + ' / ' + str(record.date)
            record.name = name

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        """Method to onchange vehicle."""
        if self.vehicle_id:
            odometer_unit = self.vehicle_id.odometer_unit
            value = self.vehicle_id.odometer
            self.unit = odometer_unit
            self.value = value

    name = fields.Char(compute="_compute_vehicle_log_name_get_fnc", string='Nom',
                       store=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    value = fields.Float(string='Valeur du compteur kilométrique', group_operator="max")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicule',
                                 required=True)
    make = fields.Many2one(related='vehicle_id.f_brand_id',
                           string='Marque', store=True)
    model = fields.Many2one(related='vehicle_id.model_id',
                            string='Modèle', store=True)
    unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit",
                            readonly=True)

    @api.model
    def default_get(self, fields):
        """Method default get."""
        res = super(FleetVehicleOdometer, self).default_get(fields)
        # cr, uid, context = self.env.args
        context = self.env.context
        # context = dict(context)
        fleet_obj = self.env['fleet.vehicle']
        if self._context.get('active_id'):
            vehicle_id = fleet_obj.browse(context['active_id'])
            if vehicle_id.state == 'write-off':
                res['vehicle_id'] = False
        return res


class ReportHeading(models.Model):
    """Model Report Heading."""

    _name = 'report.heading'
    _description = 'En-tête du rapport'

    @api.depends('image')
    def _get_image(self):
        return dict((p.id, tools.image_get_resized_images(p.image))
                    for p in self)

    def _set_image(self):
        if self.image_small:
            self.image = \
                tools.image_resize_image_small(self.image_small,
                                               size=(102, 50))
        elif self.image_medium:
            self.image = \
                tools.image_resize_image_small(self.image_medium,
                                               size=(102, 50))

    name = fields.Char(string='Title', size=128, translate=True)
    revision_no = fields.Char(string='Revision No.', size=64, translate=True)
    document_no = fields.Char(string='Document No.', size=64, translate=True)
    image = fields.Binary(string="Image",
                          help="Ce champ contient l'image utilisée comme image \
                            pour le Report , limité à 1024x1024px.")
    image_medium = fields.Binary(compute="_get_image", inverse='_set_image',
                                 string="Image de taille moyenne",
                                 help="Image de taille moyenne du rapport. \
                                 Il est automatiquement redimensionné en 128x128px \
                                image, avec un rapport d'aspect conservé, "
                                      "uniquement lorsque l'image dépasse l'un de ces \
                                 tailles. Utilisez ce champ dans les vues de formulaire ou \
                                 quelques vues kanban.")
    image_small = fields.Binary(compute="_get_image", inverse='_set_image',
                                string="Image de rapport",
                                help="Image de petite taille du rapport. \
                                C'est automatiquement "
                                     "redimensionné en image 64x64px, \
                                avec rapport d'aspect conservé. "
                                     "Utilisez ce champ partout où un petit \
                                l'image est requise.")


class ResCompany(models.Model):
    """Model Res Company."""

    _inherit = 'res.company'

    name = fields.Char(related='partner_id.name', string='Nom de l\'entreprise',
                       required=True, store=True, translate=True)


class InsuranceType(models.Model):
    """Model Insurance Type."""

    _name = 'insurance.type'
    _description = 'Type d\'assurance du véhicule'

    name = fields.Char(string='Nom')
