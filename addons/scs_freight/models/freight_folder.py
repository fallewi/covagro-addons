from odoo import fields, models, api, _
import dateutil.parser
import datetime
import time


class Folder(models.Model):
    _name = 'freight.folder'
    _rec_name = 'ref'

    ref = fields.Char(string='Référence', required=True, readonly=True, default=lambda self: _('New'))
    name = fields.Char(string="Nom", copy=False)
    category_id = fields.Many2one("freight.category", string="Catégorie", required=False)
    directory_number = fields.Char(string="Référence de répertoire", required=False)
    closing_date = fields.Date(string="Date de clôture estimée", required=False)
    state = fields.Selection([('open', 'Ouvert'), ('closed', 'Fermé')], string="Statut", default='open')
    act_credit = fields.Float(string="Crédit réel", compute="_compute_credit", required=False, default=0.00)
    act_debit = fields.Float(string="Débit réel", compute="_compute_debit", required=False, default=0.00)
    act_pl = fields.Float(string="PL", compute="_compute_pl", required=False, default=0.00)

    operation_ids = fields.One2many(
        comodel_name='freight.operation',
        inverse_name='folder_id',
        string='Operations',
        required=False,
        rreadonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('freight.folder.sequence') or _('New')
        result = super(Folder, self).create(vals)
        return result

    def close_folder(self):
        self.state = 'closed'

    def open_folder(self):
        self.state = 'open'

    def _compute_debit(self):
        self.act_debit = 0.00
        for rec in self:
            for operation in rec.operation_ids:
                bills = self.env["account.move"].search(
                    [
                        ("operation_id", "=", operation.id),
                        ("move_type", "=", "in_invoice"),
                        ("state", "not in", ["cancel"]),
                    ]
                )
                rec.act_debit += sum(bills.mapped("amount_total"))

    def _compute_credit(self):
        self.act_credit = 0.00
        for rec in self:
            for operation in rec.operation_ids:
                invs = self.env["account.move"].search(
                    [
                        ("operation_id", "=", operation.id),
                        ("move_type", "=", "out_invoice"),
                        ("state", "not in", ["cancel"]),
                    ]
                )
                rec.act_credit += sum(invs.mapped("amount_total"))

    def _compute_pl(self):
        self.act_pl = 0.00
        for rec in self:
            rec.act_pl = rec.act_credit - rec.act_debit

    def action_open_invoices(self):
       return {
           'name': _("Invoices"),
           'type': 'ir.actions.act_window',
           'view_mode': 'tree,form',
           'res_model': 'account.move.line',
           'domain': [('move_id.operation_id.folder_id', '=', self.id), ('move_id.move_type', '=', 'out_invoice')],
           'target': 'current',
       }

    def action_open_bills(self):
       return {
           'name': _("Bills"),
           'type': 'ir.actions.act_window',
           'view_mode': 'tree,form',
           'res_model': 'account.move.line',
           'domain': [('move_id.operation_id.folder_id', '=', self.id), ('move_id.move_type', '=', 'in_invoice')],
           'target': 'current',
       }