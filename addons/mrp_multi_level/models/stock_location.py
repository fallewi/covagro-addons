# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    mrp_area_id = fields.Many2one(
        comodel_name="mrp.area",
        string="Zone de fabrication",
        help="Les exigences pour une zone de fabrication particulière sont combinées pour les "
        "fins de passation des marchés par le MRP.",
    )
