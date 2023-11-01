# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from random import randint

from odoo import fields, models


class MrpTag(models.Model):
    _name = "mrp.tag"
    _description = "Étiquettes de fabrications"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Nom de l'Étiquette", required=True, translate=True)
    color = fields.Integer("Couleur de l'Étiquette", default=_get_default_color)

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Le nom de l'étiquette existe déjà !"),
    ]
