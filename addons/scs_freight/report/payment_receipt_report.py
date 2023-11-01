# See LICENSE file for full copyright and licensing details.
"""Payment Receipt Report AbstractModel."""

from odoo import _, api, models
from odoo.exceptions import UserError


class InvPaymentReceiptReport(models.AbstractModel):
    """Payment Receipt Report AbstractModel."""

    _name = "report.scs_freight.inv_payment_receipt_report"
    _description = "Signaler un reçu de paiement de facture"

    def get_payment_details(self, invoice=False):
        """Method to get the invoice payment details."""
        vals = []
        payment_vals = invoice.sudo()._get_reconciled_info_JSON_values()
        for data in payment_vals:
            partial_payment = {
                "payment_date": data.get("date", False),
                "payment_journal_name": data.get("journal_name", False),
                "payment_amount": data.get("amount", False),
            }
            vals.append(partial_payment)
        return vals

    @api.model
    def _get_report_values(self, docids, data=None):
        """Method to render the Invoice Payment Receipt report template."""
        docs = []
        inv_obj = self.env["account.move"]
        if docids:
            invoices = inv_obj.search(
                [("operation_id", "in", docids), ("move_type", "=", "out_invoice")]
            )
            docs = self.env["freight.operation"].browse(docids)
        if not invoices:
            raise UserError(_("La commande d'expédition actuelle n'a pas de facture!!"))
        docargs = {
            "docids": docids,
            "doc_model": "freight.operation",
            "docs": docs,
            "data": data,
            "get_payment_details": self.get_payment_details,
        }
        return docargs


class BillPaymentReceiptReport(models.AbstractModel):
    """Payment Receipt Report AbstractModel."""

    _name = "report.scs_freight.bill_payment_receipt_report"
    _description = "Signaler un reçu de paiement de facture"

    def get_bill_payment_details(self, invoice=False):
        """Method to get the bill payment details."""
        vals = []
        payment_vals = invoice.sudo()._get_reconciled_info_JSON_values()
        for data in payment_vals:
            partial_payment = {
                "payment_date": data.get("date", False),
                "payment_journal_name": data.get("journal_name", False),
                "payment_amount": data.get("amount", False),
            }
            vals.append(partial_payment)
        return vals

    @api.model
    def _get_report_values(self, docids, data=None):
        """Method to render the Bill Payment Receipt report template."""
        docs = []
        inv_obj = self.env["account.move"]
        if docids:
            bills = inv_obj.search(
                [("operation_id", "in", docids), ("move_type", "=", "in_invoice")]
            )
            docs = self.env["freight.operation"].browse(docids)
        if not bills:
            raise UserError(_("La commande d'expédition actuelle n'a pas de facture!!"))
        docargs = {
            "docids": docids,
            "doc_model": "freight.operation",
            "docs": docs,
            "data": data,
            "get_bill_payment_details": self.get_bill_payment_details,
        }
        return docargs
