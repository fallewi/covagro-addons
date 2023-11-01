# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List, Union

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProductionSplitWizard(models.TransientModel):
    _name = "mrp.production.split.wizard"

    production_id = fields.Many2one(
        "mrp.production",
        "Production",
        required=True,
        ondelete="cascade",
    )
    split_mode = fields.Selection(
        [
            ("simple", "Extraire une quantité du MO d'origine"),
            ("equal", "Extraire une quantité en plusieurs MO de quantités égales"),
            ("custom", "Méthode différente"),
        ],
        required=True,
        default="simple",
    )
    split_qty = fields.Float(
        string="Quantity",
        digits="Unité de mesure du produit",
        help="Quantité totale à extraire du MO d'origine.",
    )
    split_equal_qty = fields.Float(
        string="Quantité égale",
        digits="Unité de mesure du produit",
        help="Utilisé pour diviser le MO en plusieurs MO avec des quantités égales.",
        default=1,
    )
    custom_quantities = fields.Char(
        string="Quantités fractionnées",
        help="Liste des quantités séparées par des espaces à fractionner :\n"
        "par exemple, '3 2 5' donnera 3 MO avec respectivement 3, 2 et 5 unités.\n"
        "Si la somme des quantités est inférieure à la quantité du MO d'origine, le "
        "la quantité restante restera dans le MO d'origine.",
    )
    product_tracking = fields.Selection(related="production_id.product_id.tracking")
    product_uom_id = fields.Many2one(related="production_id.product_uom_id")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        # Auto-complete production_id from context
        if "production_id" in fields_list and active_model == "mrp.production":
            res["production_id"] = active_id
        # Auto-complete split_mode from production_id
        if "split_mode" in fields_list and res.get("production_id"):
            production = self.env["mrp.production"].browse(res["production_id"])
            if production.product_tracking == "serial":
                res["split_mode"] = "equal"
        # Auto-complete split_qty from production_id
        if "split_qty" in fields_list and res.get("production_id"):
            production = self.env["mrp.production"].browse(res["production_id"])
            res["split_qty"] = production._get_quantity_to_backorder()
        return res

    @api.model
    def _parse_float(self, value: Union[float, int, str]) -> float:
        """Parse a float number from a string, with the user's language settings."""
        if isinstance(value, (float, int)):  # pragma: no cover
            return float(value)
        lang = self.env["res.lang"]._lang_get(self.env.user.lang)
        try:
            return float(
                value.replace(lang.thousands_sep, "")
                .replace(lang.decimal_point, ".")
                .strip()
            )
        except ValueError as e:  # pragma: no cover
            raise UserError(_("%s n'est pas un nombre.", value)) from e

    @api.model
    def _parse_float_list(self, value: str) -> List[float]:
        """Parse a list of float numbers from a string."""
        return [self._parse_float(v) for v in value.split()]

    @api.onchange("custom_quantities")
    def _onchange_custom_quantities_check(self):
        """Check that the custom quantities are valid."""
        if self.custom_quantities:  # pragma: no cover
            try:
                self._parse_float_list(self.custom_quantities)
            except UserError:
                return {
                    "warning": {
                        "title": _("Quantités invalides"),
                        "message": _("Veuillez saisir une liste de chiffres séparés par des espaces."),
                    }
                }

    def _get_split_quantities(self) -> List[float]:
        """Return the quantities to split, according to the settings."""
        production = self.production_id
        rounding = production.product_uom_id.rounding
        if self.split_mode == "simple":
            if (
                fields.Float.compare(
                    self.split_qty, production._get_quantity_to_backorder(), rounding
                )
                > 0
            ):
                raise UserError(_("Vous ne pouvez pas fractionner des quantités déjà en production."))
            if fields.Float.is_zero(self.split_qty, precision_rounding=rounding):
                raise UserError(_("Rien à diviser."))
            return [production.product_qty - self.split_qty, self.split_qty]
        elif self.split_mode == "equal":
            split_total = min(production._get_quantity_to_backorder(), self.split_qty)
            split_count = int(split_total // self.split_equal_qty)
            split_rest = production.product_qty - split_total
            split_rest += split_total % self.split_equal_qty
            quantities = [self.split_equal_qty] * split_count
            if not fields.Float.is_zero(split_rest, precision_rounding=rounding):
                quantities = [split_rest] + quantities
            return quantities
        elif self.split_mode == "custom":
            quantities = self._parse_float_list(self.custom_quantities)
            split_total = sum(quantities)
            split_rest = production.product_qty - split_total
            if not fields.Float.is_zero(split_rest, precision_rounding=rounding):
                quantities = [split_rest] + quantities
            return quantities
        else:  # pragma: no cover
            raise UserError(_("Mode de division invalide: '%s'", self.split_mode))

    def _apply(self):
        self.ensure_one()
        records = self.production_id.with_context(
            copy_date_planned=True
        )._split_productions(
            amounts={self.production_id: self._get_split_quantities()},
            cancel_remaning_qty=False,
            set_consumed_qty=False,
        )
        new_records = records - self.production_id
        for record in new_records:
            record.message_post_with_view(
                "mail.message_origin_link",
                values=dict(self=record, origin=self.production_id),
                message_log=True,
            )
        if new_records:
            self.production_id.message_post_with_view(
                "mrp_production_split.message_order_split",
                values=dict(self=self.production_id, records=new_records),
                message_log=True,
            )
        return records

    def apply(self):
        records = self._apply()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_production_action"
        )
        action["domain"] = [("id", "in", records.ids)]
        return action
