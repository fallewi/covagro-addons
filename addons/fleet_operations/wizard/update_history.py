# See LICENSE file for full copyright and licensing details.
"""Update History Wizard."""

from datetime import datetime

from odoo import api, fields, models

from odoo.exceptions import ValidationError


class UpdateEngineInfo(models.TransientModel):
    """Update Engine Info."""

    _name = 'update.engine.info'
    _description = 'Update Engine Info'

    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')
    previous_engine_no = fields.Char(string='No du Moteur précédent ',
                                     translate=True)
    new_engine_no = fields.Char(string="No du Nouveau moteur",
                                translate=True)
    changed_date = fields.Date(string='Date de modification',
                               default=fields.Date.today())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Temp Bool pour faire \
                                    couleur précédente en lecture seule')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")

    @api.constrains('changed_date')
    def check_engine_changed_date(self):
        """Method to check engine date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.vehicle_id.acquisition_date:
                if vehicle.changed_date < vehicle.vehicle_id.acquisition_date:
                    raise ValidationError('La date de changement de moteur doit être '
                                          'Supérieur à la date d\'immatriculation du véhicule.')

    @api.model
    def default_get(self, fields):
        """Method Default Get."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateEngineInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_engine_no': vehicle.engine_no or "",
                'vehicle_id': vehicle.id or False
            })
        return res

    def set_new_engine_info(self):
        """Method set new engine info."""
        vehicle_obj = self.env['fleet.vehicle']
        engine_history_obj = self.env['engine.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({'engine_no': wiz_data.new_engine_no or ""})
                engine_history_obj.create({
                    'previous_engine_no': wiz_data.previous_engine_no or "",
                    'new_engine_no': wiz_data.new_engine_no or "",
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id and
                                    wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True


class UpdateColorInfo(models.TransientModel):
    """Update Color Info."""

    _name = 'update.color.info'
    _description = 'Mettre à jour les informations de couleur'

    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')
    previous_color_id = fields.Many2one('color.color', string="Couleur précédente")
    current_color_id = fields.Many2one('color.color', string="Nouvelle couleur")
    changed_date = fields.Date(string='Date de modification',
                               default=fields.Date.today())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Booléen pour mettre les précédents couleurs en lecture seule')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")

    @api.constrains('changed_date')
    def check_color_changed_date(self):
        """Method to check color changed date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.vehicle_id.acquisition_date:
                if vehicle.changed_date < vehicle.vehicle_id.acquisition_date:
                    raise ValidationError('La date de changement de couleur doit être '
                                          'Supérieur à la date d\'immatriculation du véhicule.')

    @api.model
    def default_get(self, fields):
        """Method default Get."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateColorInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_color_id': vehicle.vehical_color_id.id or False,
                'vehicle_id': vehicle.id or False
            })
        return res

    def set_new_color_info(self):
        """Method set new color info."""
        vehicle_obj = self.env['fleet.vehicle']
        color_history_obj = self.env['color.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'vehical_color_id': wiz_data.current_color_id.id or False
                })
                color_history_obj.create({
                    'previous_color_id': wiz_data.previous_color_id.id or False,
                    'current_color_id': wiz_data.current_color_id.id or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True


class UpdateVinInfo(models.TransientModel):
    """Update Vin Info."""

    _name = 'update.vin.info'
    _description = 'Update Vin Info'

    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')
    previous_vin_no = fields.Char(string='Numéro de vin précédent')
    new_vin_no = fields.Char(string="Nouveau Numéro de vin")
    changed_date = fields.Date(default=fields.Date.today(),
                               string='Date de modification')
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Booléen pour mettre les précédents VIN en lecture seule')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")

    @api.model
    def default_get(self, fields):
        """Method default get."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateVinInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_vin_no': vehicle.vin_sn or "",
                'vehicle_id': vehicle.id
            })
        return res

    def set_new_vin_info(self):
        """Method to set new vin info."""
        vehicle_obj = self.env['fleet.vehicle']
        vin_history_obj = self.env['vin.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({'vin_sn': wiz_data.new_vin_no or ""})
                vin_history_obj.create({
                    'previous_vin_no': wiz_data.previous_vin_no or "",
                    'new_vin_no': wiz_data.new_vin_no or "",
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True


class UpdateTireInfo(models.TransientModel):
    """Update Tire Info."""

    _name = 'update.tire.info'
    _description = 'Update Tire Info'

    previous_tire_size = fields.Char(string='Taille de pneu précédente')
    new_tire_size = fields.Char(string="Nouvelle taille de pneu")
    previous_tire_sn = fields.Char(string='Numéro de série du pneu précédent')
    new_tire_sn = fields.Char(string="Nouveau pneu S/N")
    previous_tire_issue_date = fields.Date(
        string='Date d\'émission du pneu précédent')
    new_tire_issue_date = fields.Date(string='Date d\'émission du nouveau pneu')
    changed_date = fields.Date(string='Date de modification',
                               default=fields.Date.today())
    note = fields.Text('Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Booléen pour mettre les précédents pneus en lecture seule')
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")

    @api.constrains('previous_tire_issue_date', 'new_tire_issue_date')
    def check_new_tire_issue_date(self):
        """Method to check new tire issue date."""
        for vehicle in self:
            if vehicle.previous_tire_issue_date and vehicle.new_tire_issue_date \
                    and vehicle.new_tire_issue_date < vehicle.previous_tire_issue_date:
                raise ValidationError('La date d\'émission du nouveau pneu doit être '
                                      'Supérieur à la date d\'émission des pneus précédente.')

    @api.constrains('changed_date', 'new_tire_issue_date')
    def check_tire_changed_date(self):
        """Method to check tire changed date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_tire_issue_date and \
                    vehicle.changed_date < vehicle.new_tire_issue_date:
                raise ValidationError('La date de modification du pneu doit être '
                                      'Supérieur à la date d\'émission du pneu neuf.')

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateTireInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_tire_size': vehicle.tire_size or "",
                'previous_tire_sn': vehicle.tire_srno or "",
                "previous_tire_issue_date": vehicle.tire_issuance_date,
                'vehicle_id': vehicle.id
            })
        return res

    def set_new_tire_info(self):
        """Method set new tire info."""
        vehicle_obj = self.env['fleet.vehicle']
        tire_history_obj = self.env['tire.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'tire_size': wiz_data.new_tire_size or "",
                    'tire_srno': wiz_data.new_tire_sn or "",
                    'tire_issuance_date': wiz_data.new_tire_issue_date
                })
                tire_history_obj.create({
                    'previous_tire_size': wiz_data.previous_tire_size or "",
                    'new_tire_size': wiz_data.new_tire_size or "",
                    'previous_tire_sn': wiz_data.previous_tire_sn or "",
                    'new_tire_sn': wiz_data.new_tire_sn or "",
                    'previous_tire_issue_date':
                        wiz_data.previous_tire_issue_date or False,
                    'new_tire_issue_date':
                        wiz_data.new_tire_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True


class UpdateBatteryInfo(models.TransientModel):
    """Update Battery Info."""

    _name = 'update.battery.info'
    _description = 'Update Battery Info'

    previous_battery_size = fields.Char(string='Taille de la batterie précédente')
    new_battery_size = fields.Char(string="Nouvelle taille de batterie")
    previous_battery_sn = fields.Char(string='Numéro de série de la batterie précédente')
    new_battery_sn = fields.Char(string="Nouvelle batterie S/N")
    previous_battery_issue_date = fields.Date(
        string='Date d\'émission de la batterie précédente')
    new_battery_issue_date = fields.Date(string='Date d\'émission de la nouvelle batterie')
    changed_date = fields.Date(string='Date de modification',
                               default=fields.Date.today())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True,
                               string='Booléen pour mettre  les Informations précédentes  sur la batterie en lecture seule')
    workorder_id = fields.Many2one('fleet.vehicle.log.services',
                                   string='Demande de service')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")

    @api.constrains('previous_battery_issue_date', 'new_battery_issue_date')
    def check_new_battery_issue_date(self):
        """Method to check new battery issue date."""
        for vehicle in self:
            if vehicle.previous_battery_issue_date and vehicle.new_battery_issue_date and \
                    vehicle.new_battery_issue_date < vehicle.previous_battery_issue_date:
                raise ValidationError('La nouvelle date d\'émission de la batterie doit être '
                                      'Supérieur à la date d\'émission de la batterie précédente.')

    @api.constrains('changed_date', 'new_battery_issue_date')
    def check_battery_changed_date(self):
        """Method to check battery changed date."""
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_battery_issue_date \
                    and vehicle.changed_date < vehicle.new_battery_issue_date:
                raise ValidationError('La date de modification de la batterie doit être '
                                      'Supérieur à la date d\'émission de la nouvelle batterie.')

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateBatteryInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_battery_size': vehicle.battery_size or "",
                'previous_battery_sn': vehicle.battery_srno or "",
                "previous_battery_issue_date": vehicle.battery_issuance_date,
                'vehicle_id': vehicle.id
            })
        return res

    def set_new_battery_info(self):
        """Method to set new battery info."""
        vehicle_obj = self.env['fleet.vehicle']
        battery_history_obj = self.env['battery.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'battery_size': wiz_data.new_battery_size or "",
                    'battery_srno': wiz_data.new_battery_sn or "",
                    'battery_issuance_date': wiz_data.new_battery_issue_date
                })
                battery_history_obj.create({
                    'previous_battery_size':
                        wiz_data.previous_battery_size or "",
                    'new_battery_size': wiz_data.new_battery_size or "",
                    'previous_battery_sn': wiz_data.previous_battery_sn or "",
                    'new_battery_sn': wiz_data.new_battery_sn or "",
                    'previous_battery_issue_date':
                        wiz_data.previous_battery_issue_date or False,
                    'new_battery_issue_date':
                        wiz_data.new_battery_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True
