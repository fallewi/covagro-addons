# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
import re

from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json
import io
from odoo.tools import date_utils
import base64

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}


class InsFinancialReport(models.TransientModel):
    _name = "ins.financial.report"
    _description = "Financial Reports"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.journal_ids = self.env['account.journal'].search(
                [('company_id', '=', self.company_id.id)])
        else:
            self.journal_ids = self.env['account.journal'].search([])

    @api.onchange('date_range', 'financial_year')
    def onchange_date_range(self):
        if self.date_range:
            date = datetime.today()
            if self.date_range == 'today':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            if self.date_range == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
            if self.date_range == 'this_month':
                self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            if self.date_range == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            if self.date_range == 'this_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=1))
            if self.date_range == 'yesterday':
                self.date_from = date.strftime("%Y-%m-%d")
                self.date_to = date.strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(days=7))
            if self.date_range == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                self.date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                self.date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=1))
            if self.date_range == 'last_month':
                self.date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                self.date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(months=3))
            if self.date_range == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    self.date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
            date = (datetime.now() - relativedelta(years=1))
            if self.date_range == 'last_financial_year':
                if self.financial_year == 'january_december':
                    self.date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    self.date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'april_march':
                    if date.month < 4:
                        self.date_from = datetime(date.year - 1, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 3, 31).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 3, 31).strftime("%Y-%m-%d")
                if self.financial_year == 'july_june':
                    if date.month < 7:
                        self.date_from = datetime(date.year - 1, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year, 6, 30).strftime("%Y-%m-%d")
                    else:
                        self.date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                        self.date_to = datetime(date.year + 1, 6, 30).strftime("%Y-%m-%d")


    def _compute_account_balance(self, accounts, report):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0') and self.strict_range:

                context = dict(self._context, strict_range=True)
                # Validation
                if report.type in ['accounts','account_type'] and not report.range_selection:
                    raise UserError(_('Please choose "Custom Date Range" for the report head %s')%(report.name))

                if report.type in ['accounts','account_type'] and report.range_selection == 'from_the_beginning':
                    context.update({'strict_range': False})
                # For equity
                if report.type in ['accounts','account_type'] and report.range_selection == 'current_date_range':
                    if self.date_to and self.date_from:
                        context.update({'strict_range': True, 'initial_bal': False, 'date_from': self.date_from,'date_to': self.date_to})
                    else:
                        raise UserError(_('From date and To date are mandatory to generate this report'))
                if report.type in ['accounts','account_type'] and report.range_selection == 'initial_date_range':
                    if self.date_from:
                        context.update({'strict_range': True, 'initial_bal': True, 'date_from': self.date_from,'date_to': False})
                    else:
                        raise UserError(_('From date is mandatory to generate this report'))
                tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
            else:
                tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res[report.id]['account'] = self._compute_account_balance(report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
                else:
                    res2 = self._compute_report_balance(report.parent_id)
                    for key, value in res2.items():
                        if report in [self.env.ref('account_dynamic_reports.ins_cash_in_operation_1'),
                                        self.env.ref('account_dynamic_reports.ins_cash_in_investing_1'),
                                      self.env.ref('account_dynamic_reports.ins_cash_in_financial_1')]:
                            res[report.id]['debit'] += value['debit']
                            res[report.id]['balance'] += value['debit']
                        else:
                            res[report.id]['credit'] += value['credit']
                            res[report.id]['balance'] += -(value['credit'])
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
                    res[report.id]['account'] = self._compute_account_balance(accounts, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
                else:
                    accounts = self.env['account.account'].search(
                        [('user_type_id', 'in', report.account_type_ids.ids)])
                    res[report.id]['account'] = self._compute_account_balance(
                        accounts, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance(report.account_report_id)
                    for key, value in res2.items():
                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    res[report.id]['account'] = self._compute_account_balance(
                        report.account_ids, report)
                    for value in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += value.get(field)
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                if self.account_report_id != \
                        self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                    res2 = self._compute_report_balance(report.children_ids)
                    for key, value in res2.items():
                        for field in fields:
                            res[report.id][field] += value[field]
                else:
                    accounts = report.account_ids
                    if report == self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
                        accounts = self.env['account.account'].search([('company_id','=', self.env.company.id),
                                                                       ('cash_flow_category', 'not in', [0])])
                    res[report.id]['account'] = self._compute_account_balance(accounts, report)
                    for values in res[report.id]['account'].values():
                        for field in fields:
                            res[report.id][field] += values.get(field)
        return res

    def get_account_lines(self, data):
        lines = []
        initial_balance = 0.0
        current_balance = 0.0
        ending_balance = 0.0
        account_report = self.account_report_id
        child_reports = account_report._get_children_by_order(strict_range = self.strict_range)
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            if not data.get('used_context').get('date_from',False):
                raise UserError(_('Start date is mandatory!'))
            cashflow_context = data.get('used_context')
            initial_to = fields.Date.from_string(data.get('used_context').get('date_from')) - timedelta(days=1)
            cashflow_context.update({'date_from': False, 'date_to': fields.Date.to_string(initial_to)})
            initial_balance = self.with_context(cashflow_context)._compute_report_balance(child_reports). \
                get(self.account_report_id.id)['balance']
            current_balance = res.get(self.account_report_id.id)['balance']
            ending_balance = initial_balance + current_balance
        if data['enable_filter']:
            comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']

        for report in child_reports:
            company_id = self.env.company
            currency_id = company_id.currency_id
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * int(report.sign),
                'parent': report.parent_id.id if report.parent_id.type in ['accounts','account_type'] else 0,
                'self_id': report.id,
                'type': 'report',
                'style_type': 'main',
                'precision': currency_id.decimal_places,
                'symbol': currency_id.symbol,
                'position': currency_id.position,
                'list_len': [a for a in range(0,report.level)],
                'level': report.level,
                'company_currency_id': self.env.company.currency_id.id,
                'account_type': report.type or False, #used to underline the financial report balances
                'fin_report_type': report.type,
                'display_detail': report.display_detail
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * int(report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                continue

            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'account': account.id,
                        'name': account.code + ' ' + account.name,
                        'balance': value['balance'] * int(report.sign) or 0.0,
                        'type': 'account',
                        'parent': report.id if report.type in ['accounts','account_type'] else 0,
                        'self_id': 50,
                        'style_type': 'sub',
                        'precision': currency_id.decimal_places,
                        'symbol': currency_id.symbol,
                        'position': currency_id.position,
                        'list_len':[a for a in range(0, report.level)],
                        'level': report.level + 1,
                        'company_currency_id': self.env.company.currency_id.id,
                        'account_type': account.internal_type,
                        'fin_report_type': report.type,
                        'display_detail': report.display_detail
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if not currency_id.is_zero(vals['debit']) or not currency_id.is_zero(vals['credit']):
                            flag = True
                    if not currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * int(report.sign)
                        if not currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines, initial_balance, current_balance, ending_balance

    def get_report_values(self):
        self.ensure_one()

        self.onchange_date_range()

        company_domain = [('company_id', '=', self.env.company.id)]

        journal_ids = self.env['account.journal'].search(company_domain)
        analytics = self.env['account.analytic.account'].search(company_domain)
        analytic_tags = self.env['account.analytic.tag'].sudo().search(
            ['|', ('company_id', '=', self.env.company.id), ('company_id', '=', False)])

        data = dict()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'enable_filter', 'debit_credit', 'date_to', 'date_range',
             'account_report_id', 'target_move', 'view_format', 'journal_ids',
             'analytic_ids', 'analytic_tag_ids', 'strict_range',
             'company_id','enable_filter','date_from_cmp','date_to_cmp','label_filter','filter_cmp'])[0]
        data['form'].update({'journals_list': [(j.id, j.name) for j in journal_ids]})
        data['form'].update({'analytics_list': [(j.id, j.name) for j in analytics]})
        data['form'].update({'analytic_tag_list': [(j.id, j.name) for j in analytic_tags]})

        if self.enable_filter:
            data['form']['debit_credit'] = False

        date_from, date_to = False, False
        used_context = {}
        used_context['date_from'] = self.date_from or False
        used_context['date_to'] = self.date_to or False

        used_context['strict_range'] = True
        used_context['company_id'] = self.env.company.id

        used_context['journal_ids'] = self.journal_ids.ids
        used_context['analytic_account_ids'] = self.analytic_ids
        used_context['analytic_tag_ids'] = self.analytic_tag_ids
        used_context['state'] = data['form'].get('target_move', '')
        data['form']['used_context'] = used_context

        comparison_context = {}
        comparison_context['strict_range'] = True
        comparison_context['company_id'] = self.env.company.id

        comparison_context['journal_ids'] = self.journal_ids.ids
        comparison_context['analytic_account_ids'] = self.analytic_ids
        comparison_context['analytic_tag_ids'] = self.analytic_tag_ids
        if self.filter_cmp == 'filter_date':
            comparison_context['date_to'] = self.date_to_cmp or ''
            comparison_context['date_from'] = self.date_from_cmp or ''
        else:
            comparison_context['date_to'] = False
            comparison_context['date_from'] = False
        comparison_context['state'] = self.target_move or ''
        data['form']['comparison_context'] = comparison_context

        report_lines, initial_balance, current_balance, ending_balance = self.get_account_lines(data.get('form'))
        data['currency'] = self.env.company.currency_id.id
        data['report_lines'] = report_lines
        data['initial_balance'] = initial_balance or 0.0
        data['current_balance'] = current_balance or 0.0
        data['ending_balance'] = ending_balance or 0.0
        if self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_cash_flow0'):
            data['form']['rtype'] = 'CASH'
        elif self.account_report_id == \
                self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0'):
            data['form']['rtype'] = 'PANDL'
        else:
            if self.strict_range:
                data['form']['rtype'] = 'OTHER'
            else:
                data['form']['rtype'] = 'PANDL'
        return data

    @api.model
    def _get_default_report_id(self):
        if self.env.context.get('report_name', False):
            return self.env.context.get('report_name', False)
        return self.env.ref('account_dynamic_reports.ins_account_financial_report_profitandloss0').id

    @api.model
    def _get_default_date_range(self):
        return self.env.company.date_range

    @api.depends('account_report_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.account_report_id.name or 'Financial Report'
            res.append((record.id, name))
        return res

    financial_year = fields.Selection(
        [('april_march', '1 April to 31 March'),
         ('july_june', '1 july to 30 June'),
         ('january_december', '1 Jan to 31 Dec')],
        string='Financial Year', default=lambda self: self.env.company.financial_year, required=True)

    date_range = fields.Selection(
        [('today', 'Today'),
         ('this_week', 'This Week'),
         ('this_month', 'This Month'),
         ('this_quarter', 'This Quarter'),
         ('this_financial_year', 'This financial Year'),
         ('yesterday', 'Yesterday'),
         ('last_week', 'Last Week'),
         ('last_month', 'Last Month'),
         ('last_quarter', 'Last Quarter'),
         ('last_financial_year', 'Last Financial Year')],
        string='Date Range', default=_get_default_date_range
    )
    view_format = fields.Selection([
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal')],
        default='vertical',
        string="Format")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    strict_range = fields.Boolean(
        string='Strict Range',
        default=lambda self: self.env.company.strict_range)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search(
                                       [('company_id', '=', self.company_id.id)]))
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')

    enable_filter = fields.Boolean(
        string='Enable Comparison',
        default=False)
    account_report_id = fields.Many2one(
        'ins.account.financial.report',
        string='Account Reports',
        required=True, default=_get_default_report_id)

    debit_credit = fields.Boolean(
        string='Display Debit/Credit Columns',
        default=True,
        help="Help to identify debit and credit with balance line for better understanding.")
    analytic_ids = fields.Many2many(
        'account.analytic.account', string='Analytic Accounts'
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', string='Analytic Tags'
    )
    date_from_cmp = fields.Date(string='Start Date')
    date_to_cmp = fields.Date(string='End Date')
    filter_cmp = fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date')], string='Filter by',
                                  required=True, default='filter_date')
    label_filter = fields.Char(string='Column Label', default='Comparison Period',
                               help="This label will be displayed on report to show the balance computed for the given comparison filter.")

    @api.model
    def create(self, vals):
        ret = super(InsFinancialReport, self).create(vals)
        return ret

    def write(self, vals):

        if vals.get('date_range'):
            vals.update({'date_from': False, 'date_to': False})
        if vals.get('date_from') or vals.get('date_to'):
            vals.update({'date_range': False})

        if vals.get('journal_ids'):
            vals.update({'journal_ids': vals.get('journal_ids')})
        if vals.get('journal_ids') == []:
            vals.update({'journal_ids': [(5,)]})

        if vals.get('analytic_ids'):
            vals.update({'analytic_ids': vals.get('analytic_ids')})
        if vals.get('analytic_ids') == []:
            vals.update({'analytic_ids': [(5,)]})

        if vals.get('analytic_tag_ids'):
            vals.update({'analytic_tag_ids': vals.get('analytic_tag_ids')})
        if vals.get('analytic_tag_ids') == []:
            vals.update({'analytic_tag_ids': [(5,)]})

        ret = super(InsFinancialReport, self).write(vals)
        return ret

    def action_pdf(self):
        ''' Button function for Pdf '''
        data = self.get_report_values()
        return self.env.ref(
            'account_dynamic_reports.ins_financial_report_pdf').report_action(self,
                                                                     data)

    def action_xlsx(self):
        ''' Button function for Xlsx '''

        data = self.read()
        date_from = fields.Date.from_string(self.date_from).strftime(
            self.env['res.lang'].search([('code', '=', self.env.user.lang)])[0].date_format)
        date_to = fields.Date.from_string(self.date_to).strftime(
            self.env['res.lang'].search([('code', '=', self.env.user.lang)])[0].date_format)
        report = self.account_report_id.name


        return {
            'type': 'ir.actions.report',
            'data': {'model': 'ins.financial.report',
                     'options': json.dumps(data[0], default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': '%s - %s / %s' %(report, date_from , date_to),
                     },
            'report_type': 'xlsx'
        }

    def action_xlsx(self):
        data = self.read()[0]
        # Initialize
        #############################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(data['account_report_id'][1])
        sheet.set_zoom(95)
        sheet2 = workbook.add_worksheet('Filters')
        sheet2.protect()

        # Get record and data
        record = self.env['ins.financial.report'].browse(data.get('id', [])) or False
        data = record.get_report_values()

        # Formats
        ############################################################
        sheet2.set_column(0, 0, 25)
        sheet2.set_column(1, 1, 25)
        sheet2.set_column(2, 2, 25)
        sheet2.set_column(3, 3, 25)
        sheet2.set_column(4, 4, 25)
        sheet2.set_column(5, 5, 25)
        sheet2.set_column(6, 6, 25)
        sheet.freeze_panes(4, 0)
        sheet.screen_gridlines = False
        sheet2.screen_gridlines = False
        sheet2.protect()

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'border': False,
            'font': 'Arial',
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'bottom': False
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            # 'num_format': 'dd/mm/yyyy',
        })
        line_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'bottom': False
        })
        line_header_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'bottom': True
        })
        line_header_string = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'bottom': False
        })
        line_header_string_bold = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'left',
            'font': 'Arial',
            'bottom': True
        })
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_bold.num_format = currency_id.excel_format
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(data['form']['date_from'] and data['form']['date_from'])).strftime(lang_id.date_format)
        if data['form'].get('date_from'):
            sheet2.write(row_pos_2, 1, datestring, content_header_date)
        row_pos_2 += 1
        # Date to
        sheet2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(data['form']['date_to'] and data['form']['date_to'])).strftime(
            lang_id.date_format)
        if data['form'].get('date_to'):
            sheet2.write(row_pos_2, 1, datestring,
                                        content_header_date)
        row_pos_2 += 1
        if data['form']['enable_filter']:
            # Compariosn Date from
            sheet2.write(row_pos_2, 0, _('Comparison Date from'),
                                      format_header)
            datestring = fields.Date.from_string(str(data['form']['comparison_context']['date_from'] and data['form']['comparison_context'][
                    'date_from'].strftime('%Y-%m-%d')))
            if data['form']['comparison_context'].get('date_from'):
                sheet2.write(row_pos_2, 1, datestring,
                                            content_header_date)
            row_pos_2 += 1
            # Compariosn Date to
            sheet2.write(row_pos_2, 0, _('Comparison Date to'),
                                      format_header)
            datestring = fields.Date.from_string(
                str(data['form']['comparison_context']['date_to'] and data['form']['comparison_context'][
                    'date_to'].strftime('%Y-%m-%d')))
            if data['form']['comparison_context'].get('date_to'):
                sheet2.write(row_pos_2, 1, datestring,
                                            content_header_date)

        # Write Ledger details
        row_pos += 3
        if data['form']['debit_credit'] == 1:

            sheet.set_column(0, 0, 90)
            sheet.set_column(1, 1, 15)
            sheet.set_column(2, 3, 15)
            sheet.set_column(3, 3, 15)

            sheet.write(row_pos, 0, _('Name'), format_header)
            sheet.write(row_pos, 1, _('Debit'), format_header)
            sheet.write(row_pos, 2, _('Credit'), format_header)
            sheet.write(row_pos, 3, _('Balance'), format_header)

            for a in data['report_lines']:
                if a['level'] == 2:
                    row_pos += 1
                row_pos += 1
                if a.get('account', False):
                    tmp_style_str = line_header_string
                    tmp_style_num = line_header
                else:
                    tmp_style_str = line_header_string_bold
                    tmp_style_num = line_header_bold
                sheet.write(row_pos, 0, '   ' * a['level'] + a.get('name'),
                                        tmp_style_str)
                sheet.write(row_pos, 1, float(a.get('debit')), tmp_style_num)
                sheet.write(row_pos, 2, float(a.get('credit')), tmp_style_num)
                sheet.write(row_pos, 3, float(a.get('balance')), tmp_style_num)

        if data['form']['debit_credit'] != 1:

            sheet.set_column(0, 0, 105)
            sheet.set_column(1, 1, 15)
            sheet.set_column(2, 2, 15)

            sheet.write(row_pos, 0, _('Name'), format_header)
            if data['form']['enable_filter']:
                sheet.write(row_pos, 1, data['form']['label_filter'], format_header)
                sheet.write(row_pos, 2, _('Balance'), format_header)
            else:
                sheet.write(row_pos, 1, _('Balance'), format_header)

            for a in data['report_lines']:
                if a['level'] == 2:
                    row_pos += 1
                row_pos += 1
                if a.get('account', False):
                    tmp_style_str = line_header_string
                    tmp_style_num = line_header
                else:
                    tmp_style_str = line_header_string_bold
                    tmp_style_num = line_header_bold
                sheet.write(row_pos, 0, '   ' * a['level'] + a.get('name'),
                                        tmp_style_str)
                if data['form']['enable_filter']:
                    sheet.write(row_pos, 1, float(a.get('balance_cmp')), tmp_style_num)
                    sheet.write(row_pos, 2, float(a.get('balance')), tmp_style_num)
                else:
                    sheet.write(row_pos, 1, float(a.get('balance')), tmp_style_num)
        if data.get('initial_balance') or data.get('current_balance') or data.get('ending_balance'):
            row_pos += 2
            sheet.merge_range(row_pos, 1, row_pos, 2, 'Initial Cash Balance', tmp_style_num)
            sheet.write(row_pos, 3, float(data.get('initial_balance')), tmp_style_num)
            row_pos += 1
            sheet.merge_range(row_pos, 1, row_pos, 2, 'Current Cash Balance', tmp_style_num)
            sheet.write(row_pos, 3, float(data.get('current_balance')), tmp_style_num)
            row_pos += 1
            sheet.merge_range(row_pos, 1, row_pos, 2, 'Net Cash Balance', tmp_style_num)
            sheet.write(row_pos, 3, float(data.get('ending_balance')), tmp_style_num)

        # Close and return
        #################################################################
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        report_id = self.env['common.xlsx.out'].sudo().create({'filedata': result, 'filename': 'FIN.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xls' % (
                report_id.id, data['form']['account_report_id'][1]),
            'target': 'new',
        }

        output.close()

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'FR View',
            'tag': 'dynamic.fr',
            'context': {'wizard_id': self.id,
                        'account_report_id': self.account_report_id.id}
        }
        return res
