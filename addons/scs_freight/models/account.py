# See LICENSE file for full copyright and licensing details.
"""Account Model Related Operations."""

from odoo import api, fields, models


class AccountMove(models.Model):
    """Account Move(Invoice) Model."""

    _inherit = "account.move"

    operation_id = fields.Many2one("freight.operation", string="Operation")

    @api.model
    def default_get(self, fields):
        """Overridden Method to update partner id in invoice."""
        res = super(AccountMove, self).default_get(fields)
        if (self.env.context.get("default_operation_id", False) and
                self._context.get("default_move_type") == "out_invoice"):
            operation_rec = self.env["freight.operation"].browse(
                self.env.context["default_operation_id"])
            res.update({
                "partner_id": operation_rec.consignee_id and
                operation_rec.consignee_id.id or operation_rec.customer_id and
                operation_rec.customer_id.id or False
            })
        return res


class AccountMoveLine(models.Model):
    """Account Move Line(Account Invoice Line) Model."""

    _inherit = "account.move.line"

    service_id = fields.Many2one("operation.service", string="Service")
