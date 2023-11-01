# See LICENSE file for full copyright and licensing details.
"""Model for Reason to Revision of custom Clearance."""

from odoo import fields, models


class WizCustomClearanceReason(models.TransientModel):
    """Model for ask reason to Custom Revision."""

    _name = "wiz.custom.clearance.reason"
    _description = "Raison du dédouanement de l'assistant"

    reason = fields.Text("Raison")

    def action_custom_revision(self):
        """Send Clearance for Revision."""
        rev_obj = self.env["operation.custom.revision"]
        if self._context and self._context.get("active_ids", False):
            for custom in self.env["operation.custom"].browse(
                self._context.get("active_ids")
            ):
                rev_name = (
                    "Revision-"
                    + str(custom.revision_count + 1)
                    + "/Custom/"
                    + str(custom.operation_id.name)
                )
                revision = rev_obj.create(
                    {
                        "name": rev_name,
                        "operation_id": custom.operation_id
                        and custom.operation_id.id
                        or False,
                        "custom_id": custom.id or False,
                        "agent_id": custom.agent_id and custom.agent_id.id or False,
                        "date": fields.Date.context_today(self),
                        "operator_id": self.env.user and self.env.user.id or False,
                        "reason": self.reason or "",
                    }
                )
                for doc in custom.attachment_ids:
                    self.env["revision.doc"].create(
                        {"name": doc.name or "", "revision_id": revision.id}
                    )
