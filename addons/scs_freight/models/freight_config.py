# See LICENSE file for full copyright and licensing details.
"""This Module Contain information related to freight Configuration."""

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FreightPort(models.Model):
    """Ports Details."""

    _name = "freight.port"
    _description = "Détails des ports"

    name = fields.Char(string="Nom")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Pays")
    state_id = fields.Many2one(
        "res.country.state", string="Pays", domain="[('country_id', '=', country_id)]"
    )
    is_land = fields.Boolean(string="Voix Terrestre", default=True)
    is_ocean = fields.Boolean(string="Voix Marine", default=True)
    is_air = fields.Boolean(string="Voix Aerienne", default=True)
    active = fields.Boolean(string="Actif", default=True)

    @api.constrains("is_land", "is_ocean", "is_air")
    def _check_port(self):
        for port in self:
            if not port.is_land and not port.is_ocean and not port.is_air:
                raise UserError(_("Veuillez vérifier au moins un port !!"))


class FreightVessels(models.Model):
    """Vessels Details."""

    _name = "freight.vessels"
    _description = "Détails des navires (bateaux)."

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Pays")
    note = fields.Text(string="Note")
    active = fields.Boolean(string="Active", default=True)
    transport = fields.Selection(
        [("land", "Voix Terrestre"), ("ocean", "Voix Marine"), ("air", "Voix Aerienne")], default="land"
    )


class FreightAirline(models.Model):
    """Model for Airlines Details."""

    _name = "freight.airline"
    _description = "Détails de la compagnie aérienne"

    name = fields.Char(string="Nom")
    code = fields.Char(string="Code")
    country_id = fields.Many2one("res.country", string="Pays")
    icao = fields.Char(string="ICAO", help="Organisation de l'aviation civile internationale")
    active = fields.Boolean(string="Actif", default=True)


class FreightContainers(models.Model):
    """Container Details."""

    _name = "freight.container"
    _description = "Détails du conteneur"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    container_number = fields.Char(string="Numéro du Conteneur", copy=False)
    state = fields.Selection(
        [("available", "Disponible"), ("reserve", "Reservé")], default="available"
    )
    size = fields.Float(string="Taille", help="Capacité de manutention de taille maximale")
    size_uom_id = fields.Many2one("uom.uom", string="Unité")
    volume = fields.Float(string="Volume", help="Volume maximal (M3) Capacité de manutention")
    weight = fields.Float(string="Poids", help="Poids maximal (KG) Capacité de manutention")
    is_container = fields.Boolean(string="est le conteneur ?", default=True)

    @api.constrains("size", "volume", "weight")
    def _check_container_capacity(self):
        for cont in self:
            if cont.size < 0.0 or cont.volume < 0.0 or cont.weight < 0.0:
                raise UserError(_("Vous ne pouvez pas entrer de valeur négative!!"))

    @api.model
    def create(self, vals):
        """Overridden create method to add container number."""
        if vals and not vals.get("container_number", False):
            vals.update(
                {
                    "container_number": self.env["ir.sequence"].next_by_code(
                        "freight.container.sequence"
                    )
                }
            )
        return super(FreightContainers, self).create(vals)

    def write(self, vals):
        """Overridden write Method to add container number."""
        res = super(FreightContainers, self).write(vals)
        for container in self:
            if not container.container_number:
                container.container_number = self.env["ir.sequence"].next_by_code(
                    "freight.container.sequence"
                )
        return res


class OperationPriceList(models.Model):
    """Operation PriceListing."""

    _name = "operation.price.list"
    _description = "Liste des prix d'opération"

    name = fields.Char("Name")
    volume_price = fields.Float("Volume Price", help="Prix du Volume Par m3")
    weight_price = fields.Float("Weight Price", help="Prix du Poids Par KG")
    service_price = fields.Float("Prix ​​des services")

    @api.constrains("volume_price", "weight_price")
    def _check_price(self):
        for price_list in self:
            if price_list.volume_price < 0.0 or price_list.weight_price < 0.0:
                raise UserError(_("Vous ne pouvez pas entrer le prix négatif !!"))


class Category(models.Model):
    _name = 'freight.category'
    _rec_name = 'name'

    name = fields.Char(string="Nom", copy=False)
    is_company = fields.Boolean(string="Compagnie")
    is_logistic = fields.Boolean(string="logistique")
    is_operation = fields.Boolean(string="Fret")
    is_transport = fields.Boolean(string="Transport")
    is_vessel = fields.Boolean(string="Agence maritime")
    is_warehouse = fields.Boolean(string="Entreposage")


class Incoterm(models.Model):
    _name = 'freight.incoterm'
    _rec_name = 'acronym'

    acronym = fields.Char(string="Acronyme", required=True)
    name = fields.Char(string="Nom", required=True)
    description = fields.Char(string="Description")
    is_source = fields.Boolean(string="Source")
    is_destination = fields.Boolean(string="Destination")


class CustomType(models.Model):
    _name = 'freight.custom.type'

    name = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")
    operation_type = fields.Selection([('import', 'Importation'), ('export', 'Exportation')], string="Type d'opération", required=True)
    temporary_admission = fields.Boolean(string="Admission temporaire ?")
    re_export = fields.Boolean(string="Réexporter?")
