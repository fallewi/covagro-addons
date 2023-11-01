from odoo import models, api, fields, _, sql_db
from odoo.exceptions import ValidationError
from psycopg2 import ProgrammingError
from dateutil import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.ks_dashboard_ninja.common_lib.ks_date_filter_selections import ks_get_date, ks_convert_into_utc, \
    ks_convert_into_local

import json


class KsDashboardNinjaItemAdvance(models.Model):
    _inherit = 'ks_dashboard_ninja.item'

    ks_custom_query = fields.Text(string="Custom Query",
                                  help=' Fetch, combine, and compare data by generating SQL query on your own.')
    ks_data_calculation_type = fields.Selection([('custom', 'Default Query'),
                                                 ('query', 'Custom Query')], string="Data Calculation Type",
                                                default="custom")
    ks_query_result = fields.Char(compute='ks_run_query', string="Result")
    ks_xlabels = fields.Char(string="X-Labels")
    ks_ylabels = fields.Char(string="Y-Labels")
    ks_model_id = fields.Many2one('ir.model', string='Model', required=False,
                                  domain="[('access_ids','!=',False),('transient','=',False),"
                                         "('model','not ilike','base_import%'),'|',('model','not ilike','ir.%'),('model','=ilike','_%ir.%'),"
                                         "('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),"
                                         "('model','!=','mail.thread'),('model','not ilike','ks_dash%'), ('model','not ilike','ks_to%')]")

    ks_list_view_layout = fields.Selection([('layout_1', 'Default layout'),
                                            ('layout_2', 'Layout 1'),
                                            ('layout_3', 'Layout 2'),
                                            ('layout_4', 'Layout 3')], string="List View Layout",
                                           default="layout_1")

    ks_is_date_ranges = fields.Boolean('Date Ranges',
                                       help=' Checkbox to apply default date range filter. The date filter applied will also reflect on the main page.')
    ks_query_start_date = fields.Datetime()
    ks_query_end_date = fields.Datetime()

    @api.depends('ks_dashboard_item_type', 'ks_goal_enable', 'ks_standard_goal_value', 'ks_record_count',
                 'ks_record_count_2', 'ks_previous_period', 'ks_compare_period', 'ks_year_period',
                 'ks_compare_period_2', 'ks_year_period_2', 'ks_domain_extension_2', 'ks_custom_query',
                 'ks_data_calculation_type')
    def ks_get_kpi_data(self):
        for rec in self:
            rec.ks_kpi_data = rec._ksGetKpiData(domain1=[], domain2=[])

    def _ksGetKpiData(self, domain1=[], domain2=[]):
        rec = self
        if rec.ks_dashboard_item_type and rec.ks_dashboard_item_type == 'ks_kpi':
            if rec.ks_data_calculation_type != 'query':
                return super(KsDashboardNinjaItemAdvance, self)._ksGetKpiData(domain1=domain1, domain2=domain2)
            elif rec.ks_data_calculation_type == 'query' and rec.ks_query_result:
                ks_kpi_data = json.loads(rec.ks_query_result)
                ks_data_list = [{'record_field': False, 'record_data': 0, 'model': False}]
                ks_data_list[0]['record_data'] = list(ks_kpi_data.values())[0]

                ks_kpi_data = json.dumps(ks_data_list)
            else:
                ks_kpi_data = False
        else:
            ks_kpi_data = False
        return ks_kpi_data

    @api.depends('ks_custom_query', 'ks_data_calculation_type', 'ks_query_result', 'ks_xlabels', 'ks_ylabels',
                 'ks_bar_chart_stacked')
    def ks_get_chart_data(self):
        for rec in self:
            rec.ks_chart_data = rec._ks_get_chart_data(domain=[])

    def _ks_get_chart_data(self, domain=[]):
        for rec in self:
            if rec.ks_dashboard_item_type and rec.ks_dashboard_item_type not in ['ks_tile', 'ks_list_view', 'ks_kpi']:
                if rec.ks_data_calculation_type != 'query':
                    return super(KsDashboardNinjaItemAdvance, self)._ks_get_chart_data(domain)
                else:
                    if rec.ks_query_result:
                        records = json.loads(rec.ks_query_result)
                        ks_chart_data = {'labels': [], 'domains': [], 'datasets': []}
                        if records:
                            if rec.ks_unit and rec.ks_unit_selection == 'monetary':
                                ks_chart_data['ks_selection'] = rec.ks_unit_selection
                                ks_chart_data['ks_currency'] = rec.env.user.company_id.currency_id.id
                            elif rec.ks_unit and rec.ks_unit_selection == 'custom':
                                ks_chart_data['ks_selection'] = rec.ks_unit_selection
                                if rec.ks_chart_unit:
                                    ks_chart_data['ks_field'] = rec.ks_chart_unit
                            if rec.ks_xlabels and rec.ks_ylabels:
                                ks_yaxis = json.loads(rec.ks_ylabels)

                                y_labels = []
                                for y_axis in ks_yaxis.keys():
                                    data_row = {'data': [], 'label': ks_yaxis[y_axis]['measure']}

                                    if rec.ks_dashboard_item_type in ['ks_bar_chart', 'ks_horizontalBar_chart',
                                                                      'ks_line_chart']:
                                        chart_type = ks_yaxis[y_axis]['chart_type']
                                        if chart_type in ['bar', 'line']:
                                            data_row['type'] = chart_type
                                        if rec.ks_bar_chart_stacked:
                                            data_row['stack'] = ks_yaxis[y_axis]['group']
                                        if ks_yaxis[y_axis]['chart_type'] == 'line':
                                            y_labels.insert(0, y_axis)
                                            ks_chart_data['datasets'].insert(0, data_row)
                                        else:
                                            y_labels.append(y_axis)
                                            ks_chart_data['datasets'].append(data_row)
                                    else:
                                        y_labels.append(y_axis)
                                        ks_chart_data['datasets'].append(data_row)

                                for res in records.get('records'):

                                    if res.get(rec.ks_xlabels, False):
                                        ks_chart_data['labels'].append(res[rec.ks_xlabels])
                                        counter = 0
                                        for y_axis in y_labels:
                                            ks_chart_data['datasets'][counter]['data'].append(res[y_axis])
                                            counter += 1
                        return json.dumps(ks_chart_data)

                    else:
                        return False
            else:
                return False

    @api.depends('ks_custom_query', 'ks_data_calculation_type')
    def ks_get_list_view_data(self):
        for rec in self:
            if rec.ks_list_view_type and rec.ks_dashboard_item_type and rec.ks_dashboard_item_type == 'ks_list_view':
                ks_list_view_data = {'label': [], 'data_rows': [], 'date_index': [], 'type': 'query'}
                if rec.ks_data_calculation_type != 'query':
                    return super(KsDashboardNinjaItemAdvance, self).ks_get_list_view_data()
                elif rec.ks_data_calculation_type == 'query' and rec.ks_query_result:
                    ks_list_view_data = rec.ks_format_query_result(rec.ks_query_result)
                    rec.ks_list_view_data = json.dumps(ks_list_view_data)
                else:
                    rec.ks_list_view_data = False
            else:
                rec.ks_list_view_data = False

    def _ksGetListViewData(self, domain=[]):
        rec = self
        ks_list_view_data = {'label': [], 'data_rows': [], 'date_index': [], 'type': 'query'}
        if rec.ks_list_view_type and rec.ks_dashboard_item_type and rec.ks_dashboard_item_type == 'ks_list_view':
            if rec.ks_data_calculation_type != 'query':
                return super(KsDashboardNinjaItemAdvance, self)._ksGetListViewData(domain)
            elif rec.ks_data_calculation_type == 'query' and rec.ks_query_result:
                ks_list_view_data = rec.ks_format_query_result(rec.ks_query_result)
                ks_list_view_data = json.dumps(ks_list_view_data)
            else:
                ks_list_view_data = False
        else:
            ks_list_view_data = False
        return ks_list_view_data

    def ks_format_query_result(self, ks_query_result):
        ks_list_view_data = {'label': [], 'data_rows': [], 'date_index': [], 'type': 'query'}
        query_result = json.loads(ks_query_result)
        if query_result:
            ks_list_fields = query_result.get('header')

            for field in ks_list_fields:
                field = field.replace("_", " ")
                ks_list_view_data['label'].append(field.title())
            for res in query_result.get('records'):
                data_row = {'data': [], 'ks_column_type': []}
                for field in ks_list_fields:
                    data_row['data'].append(res[field])
                    data_row['ks_column_type'].append('char')
                ks_list_view_data['data_rows'].append(data_row)

            return ks_list_view_data
        else:
            return ks_list_view_data

    @api.depends('ks_custom_query', 'ks_data_calculation_type', 'ks_query_start_date', 'ks_query_end_date',
                 'ks_is_date_ranges', 'ks_dashboard_item_type')
    def ks_run_query(self):
        selected_start_date = False
        selected_end_date = False
        ks_start_date = False
        ks_end_date = False
        if self.ks_is_date_ranges:
            ks_type = 'date'
            ks_start_date = 'ks_start_date'
            ks_end_date = 'ks_end_date'
            if self.ks_custom_query and (
                    ("%(ks_start_date)" in self.ks_custom_query) or ("%(ks_end_date)" in self.ks_custom_query)):
                ks_type = 'date'
                ks_start_date = 'ks_start_date'
                ks_end_date = 'ks_end_date'
            if self.ks_custom_query and (("%(ks_start_datetime)" in self.ks_custom_query) or (
                    "%(ks_start_datetime)" in self.ks_custom_query)):
                ks_type = 'datetime'
                ks_start_date = 'ks_start_datetime'
                ks_end_date = 'ks_end_datetime'
            if self._context.get('ksDateFilterSelection', False):
                ksDateFilterSelection = self._context.get('ksDateFilterSelection', False)

                if ksDateFilterSelection == 'l_custom':
                    ks_timezone = self._context.get('tz') or self.env.user.tz
                    selected_start_date = self._context['ksDateFilterStartDate']
                    selected_end_date = self._context['ksDateFilterEndDate']
                    ks_is_def_custom_filter = self._context.get('ksIsDefultCustomDateFilter', False)
                    if selected_start_date and selected_end_date and not ks_is_def_custom_filter and ks_type == 'datetime':
                        selected_start_date = ks_convert_into_utc(selected_start_date, ks_timezone)
                        selected_end_date = ks_convert_into_utc(selected_end_date, ks_timezone)
                    if ks_type == 'date' and ks_is_def_custom_filter:
                        selected_start_date = ks_convert_into_local(selected_start_date, ks_timezone)
                        selected_end_date = ks_convert_into_local(selected_end_date, ks_timezone)
                if ksDateFilterSelection not in ['l_custom', 'l_none']:
                    ks_get_date_ranges = ks_get_date(ksDateFilterSelection, self, ks_type)
                    selected_start_date = ks_get_date_ranges['selected_start_date']
                    selected_end_date = ks_get_date_ranges['selected_end_date']

        for rec in self:
            if rec.ks_dashboard_item_type == 'ks_bar_chart' or rec.ks_dashboard_item_type == 'ks_horizontalBar_chart':
                ks_is_group_column = True
            else:
                ks_is_group_column = False
            # with api.Environment.manage():
            ks_query = rec.ks_custom_query
            if rec.ks_data_calculation_type == 'query' and rec.ks_dashboard_item_type not in ['ks_tile', 'ks_kpi'] \
                    and rec.ks_custom_query:
                if ks_query and "{#MYCOMPANY}" in ks_query:
                    ks_query = ks_query.replace("{#MYCOMPANY}", str(self.env.company.id))
                if ks_query and "{#UID}" in ks_query:
                    ks_query = ks_query.replace("{#UID}", str(self.env.user.id))

                if rec.ks_dashboard_item_type == 'ks_list_view':
                    rec.ks_query_result = rec.ks_get_list_query_result(ks_query, selected_start_date,
                                                                       selected_end_date)
                else:
                    # with api.Environment.manage():
                    try:
                        type_code = []
                        # conn = sql_db.db_connect(self.env.cr.dbname)
                        new_env = self.pool.cursor()
                        if rec.ks_is_date_ranges:
                            start_date = rec.ks_query_start_date
                            end_date = rec.ks_query_end_date
                            if selected_end_date or selected_start_date:
                                start_date = selected_start_date if selected_start_date else selected_end_date - relativedelta.relativedelta(
                                    years=1000)
                                end_date = selected_end_date if selected_end_date else selected_start_date + relativedelta.relativedelta(
                                    years=1000)

                            new_env.execute("with ks_chart_query as (" + ks_query + ")" +
                                            "select * from ks_chart_query limit %(ks_limit)s",
                                            {ks_start_date: str(
                                                start_date - relativedelta.relativedelta(years=10)),
                                                ks_end_date: str(
                                                    end_date + relativedelta.relativedelta(years=10)),
                                                'ks_limit': 5000})
                            header_rec = [col.name for col in new_env.description]
                            result = new_env.dictfetchall()
                            if result:
                                for header_key in header_rec:
                                    if type(result[0][header_key]).__name__ == 'float' or \
                                            type(result[0][header_key]).__name__ == 'int':
                                        type_code.append('numeric')
                                    else:
                                        type_code.append('string')

                            new_env.execute("with ks_chart_query as (" + ks_query + ")" +
                                            "select * from ks_chart_query limit %(ks_limit)s",
                                            {ks_start_date: str(start_date),
                                             ks_end_date: str(end_date), 'ks_limit': 5000, })
                            header = [col.name for col in new_env.description]
                        else:
                            new_env.execute("with ks_chart_query as (" + ks_query + ")" +
                                            "select * from ks_chart_query limit %(ks_limit)s",
                                            {'ks_limit': 5000})
                            header = [col.name for col in new_env.description]

                        records = new_env.dictfetchall()
                        if records:
                            type_code.clear()
                            for header_key in header:
                                if type(records[0][header_key]).__name__ == 'float' or \
                                        type(records[0][header_key]).__name__ == 'int':
                                    type_code.append('numeric')
                                else:
                                    type_code.append('string')

                    except ProgrammingError as e:
                        if e.args[0] == 'no results to fetch':
                            raise ValidationError(_("You can only read the Data from Database"))
                        else:
                            raise ValidationError(_(e))
                    except Exception as e:
                        if type(e).__name__ == 'KeyError':
                            raise ValidationError(_(
                                'Wrong date variables, Please use ks_start_date and ks_end_date in custom query'))
                        raise ValidationError(_(e))
                    finally:
                        new_env.close()

                    for res in records:
                        for key in res:
                            if type(res[key]).__name__ == 'datetime':
                                res[key] = res[key].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            elif type(res[key]).__name__ == 'date':
                                res[key] = res[key].strftime(DEFAULT_SERVER_DATE_FORMAT)
                    rec.ks_query_result = json.dumps({'header': header,
                                                      'records': records, 'type_code': type_code,
                                                      'ks_is_group_column': ks_is_group_column})
            elif rec.ks_dashboard_item_type in ['ks_kpi'] \
                    and rec.ks_custom_query:
                if rec.ks_is_date_ranges and not (selected_start_date or selected_end_date):
                    selected_start_date = rec.ks_query_start_date
                    selected_end_date = rec.ks_query_end_date
                ks_query_result = rec.ks_get_kpi_result(ks_query, selected_start_date, selected_end_date,
                                                        ks_start_date=ks_start_date, ks_end_date=ks_end_date)

                rec.ks_query_result = json.dumps(ks_query_result)
            else:
                rec.ks_query_result = False

    def ks_get_kpi_result(self, ks_query, selected_start_date, selected_end_date, ks_start_date=False,
                          ks_end_date=False):

        new_env = self.env
        if ks_query and "{#MYCOMPANY}" in ks_query:
            ks_query = ks_query.replace("{#MYCOMPANY}", str(self.env.user.company_id.id))
        if ks_query and "{#UID}" in ks_query:
            ks_query = ks_query.replace("{#UID}", str(self.env.user.id))
        start_date = selected_start_date
        end_date = selected_end_date
        self.ks_validate_kpi_query(ks_query, start_date, end_date, ks_start_date=ks_start_date,
                                   ks_end_date=ks_end_date)
        if self.ks_is_date_ranges:

            new_env.cr.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query"
                               , {ks_start_date: str(start_date),
                                  ks_end_date: str(end_date)})
        else:
            new_env.cr.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query")

        result = new_env.cr.dictfetchone()
        if len(result.keys()) == 1:
            return result
        else:
            raise ValidationError(_("Query must be return single entity value"))

    def ks_validate_kpi_query(self, ks_query, start_date, end_date, ks_start_date=False,
                              ks_end_date=False):
        try:

            new_env = self.env
            if self.ks_is_date_ranges:
                new_env.cr.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query limit 5"
                                   , {ks_start_date: str(start_date),
                                      ks_end_date: str(end_date)})
            else:
                new_env.cr.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query limit 5")
            result = new_env.cr.dictfetchall()
            if len(result) != 1:
                raise ValidationError(_("Query must be return single entity value"))
            elif len(result[0].keys()) != 1:
                raise ValidationError(_("Query must be return single entity value"))
            else:
                ks_validate = True
        except ProgrammingError as e:
            if e.args[0] == 'no results to fetch':
                raise ValidationError(_("You can only read the Data from Database"))
            else:
                raise ValidationError(_(e))
        except Exception as e:
            if type(e).__name__ == 'KeyError':
                raise ValidationError(
                    _('Wrong date variables, Please use ks_start_date and ks_end_date in custom query'))
            raise ValidationError(_(e))


    def ks_get_list_query_result(self, ks_query, selected_start_date, selected_end_date, ks_offset=0,
                                 ks_export_all=False):
        # with api.Environment.manage():
        try:
            type_code = []
            # new_cr = self.pool.cursor()
            # conn = sql_db.db_connect(self.env.cr.dbname)
            new_env = self.pool.cursor()
            if self.ks_is_date_ranges:
                ks_start_date = 'ks_start_date'
                ks_end_date = 'ks_end_date'
                if self.ks_custom_query and (
                        ("%(ks_start_date)" in self.ks_custom_query) or ("%(ks_end_date)" in self.ks_custom_query)):
                    ks_type = 'date'
                    ks_start_date = 'ks_start_date'
                    ks_end_date = 'ks_end_date'
                if self.ks_custom_query and (("%(ks_start_datetime)" in self.ks_custom_query) or (
                        "%(ks_start_datetime)" in self.ks_custom_query)):
                    ks_type = 'datetime'
                    ks_start_date = 'ks_start_datetime'
                    ks_end_date = 'ks_end_datetime'
            limit = self.ks_pagination_limit
            if ks_query and "{#MYCOMPANY}" in ks_query:
                ks_query = ks_query.replace("{#MYCOMPANY}", str(self.env.company.id))
            if ks_query and "{#UID}" in ks_query:
                ks_query = ks_query.replace("{#UID}", str(self.env.user.id))

            if ks_export_all:
                if self._context.get('ksDateFilterSelection', False):
                    ksDateFilterSelection = self._context.get('ksDateFilterSelection', False)
                    if ksDateFilterSelection == 'l_custom':
                        ks_timezone = self._context.get('tz') or self.env.user.tz
                        selected_start_date = self._context['ksDateFilterStartDate']
                        selected_end_date = self._context['ksDateFilterEndDate']
                        ks_is_def_custom_filter = self._context.get('ksIsDefultCustomDateFilter', False)
                        if selected_start_date and selected_end_date and not ks_is_def_custom_filter and ks_type == 'datetime':
                            selected_start_date = ks_convert_into_utc(selected_start_date, ks_timezone)
                            selected_end_date = ks_convert_into_utc(selected_end_date, ks_timezone)
                        if ks_type == 'date' and ks_is_def_custom_filter:
                            selected_start_date = ks_convert_into_local(selected_start_date, ks_timezone)
                            selected_end_date = ks_convert_into_local(selected_end_date, ks_timezone)
                    if ksDateFilterSelection not in ['l_custom', 'l_none']:
                        ks_get_date_ranges = ks_get_date(ksDateFilterSelection, self, 'datetime')
                        selected_start_date = ks_get_date_ranges['selected_start_date']
                        selected_end_date = ks_get_date_ranges['selected_end_date']

            if self.ks_is_date_ranges:
                start_date = self.ks_query_start_date
                end_date = self.ks_query_end_date
                if selected_end_date or selected_start_date:
                    start_date = selected_start_date if selected_start_date else selected_end_date - relativedelta.relativedelta(
                        years=1000)
                    end_date = selected_end_date if selected_end_date else selected_start_date + relativedelta.relativedelta(
                        years=1000)

                new_env.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query limit "
                                                                             "%(ks_limit)s offset %(ks_offset)s",
                                {ks_start_date: str(start_date - relativedelta.relativedelta(years=10)),
                                 ks_end_date: str(end_date + relativedelta.relativedelta(years=10)),
                                 'ks_limit': limit, 'ks_offset': ks_offset
                                 })
                header_rec = [col.name for col in new_env.description]
                result = new_env.dictfetchall()
                if result:
                    for header_key in header_rec:
                        if type(result[0][header_key]).__name__ == 'float' or \
                                type(result[0][header_key]).__name__ == 'int':
                            type_code.append('numeric')
                        else:
                            type_code.append('string')
                if ks_export_all:
                    new_env.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query "
                                                                                 " offset %(ks_offset)s",
                                    {ks_start_date: str(start_date),
                                     ks_end_date: str(end_date),
                                     'ks_offset': ks_offset})
                else:
                    new_env.execute(
                        "with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query limit "
                                                                     "%(ks_limit)s offset %(ks_offset)s",
                        {ks_start_date: str(start_date),
                         ks_end_date: str(end_date),
                         'ks_limit': limit, 'ks_offset': ks_offset})
                header = [col.name for col in new_env.description]
            else:
                if ks_export_all:
                    new_env.execute("with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query "
                                                                                 " offset %(ks_offset)s",
                                    {'ks_offset': ks_offset})
                else:
                    new_env.execute(
                        "with ks_list_query as (" + ks_query + ")" + "select * from ks_list_query limit "
                                                                     "%(ks_limit)s offset %(ks_offset)s",
                        {'ks_limit': limit, 'ks_offset': ks_offset})
                header = [col.name for col in new_env.description]

            records = new_env.dictfetchall()
            if records:
                type_code.clear()
                for header_key in header:
                    if type(records[0][header_key]).__name__ == 'float' or \
                            type(records[0][header_key]).__name__ == 'int':
                        type_code.append('numeric')
                    else:
                        type_code.append('string')

        except ProgrammingError as e:
            if e.args[0] == 'no results to fetch':
                raise ValidationError(_("You can only read the Data from Database"))
            else:
                raise ValidationError(_(e))
        except Exception as e:
            if type(e).__name__ == 'KeyError':
                raise ValidationError(
                    _(
                        'Wrong date variables, Please use ks_start_date and ks_end_date or ks_start_datetime and ks_end_datetime in custom query'))
            raise ValidationError(_(e))
        finally:
            new_env.close()

        for res in records:
            for key in res:
                if type(res[key]).__name__ == 'datetime':
                    res[key] = res[key].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                elif type(res[key]).__name__ == 'date':
                    res[key] = res[key].strftime(DEFAULT_SERVER_DATE_FORMAT)
        return json.dumps({'header': header,
                           'records': records, 'type_code': type_code,
                           'ks_is_group_column': False})

    @api.model
    def ks_get_next_offset(self, ks_item_id, offset, item_domain=[]):
        record = self.browse(ks_item_id)
        ks_offset = offset['offset']
        selected_start_date = False
        selected_end_date = False
        if self._context.get('ksDateFilterSelection', False):
            ksDateFilterSelection = self._context.get('ksDateFilterSelection', False)
            if ksDateFilterSelection == 'l_custom':
                ks_timezone = self._context.get('tz') or self.env.user.tz
                selected_start_date = self._context['ksDateFilterStartDate']
                selected_end_date = self._context['ksDateFilterEndDate']
                selected_start_date = ks_convert_into_utc(selected_start_date, ks_timezone)
                selected_end_date = ks_convert_into_utc(selected_end_date, ks_timezone)
            if ksDateFilterSelection not in ['l_custom', 'l_none']:
                ks_get_date_ranges = ks_get_date(ksDateFilterSelection, self, 'datetime')
                selected_start_date = ks_get_date_ranges['selected_start_date']
                selected_end_date = ks_get_date_ranges['selected_end_date']
        if self.ks_data_calculation_type == 'custom':
            return super(KsDashboardNinjaItemAdvance, self).ks_get_next_offset(ks_item_id, offset, item_domain)
        else:
            ks_query = str(self.ks_custom_query)
            ks_start_date = record.ks_query_start_date
            ks_end_date = record.ks_query_end_date
            if selected_start_date or selected_end_date:
                ks_start_date = selected_start_date
                ks_end_date = selected_end_date
            ks_query_result = self.ks_get_list_query_result(ks_query, ks_start_date, ks_end_date,
                                                            ks_offset=int(ks_offset))
            ks_list_view_data = self.ks_format_query_result(ks_query_result)
        return {
            'ks_list_view_data': json.dumps(ks_list_view_data),
            'offset': int(ks_offset) + 1,
            'next_offset': int(ks_offset) + len(ks_list_view_data['data_rows']),
            'limit': record.ks_record_data_limit if record.ks_record_data_limit else 0,
        }

    @api.onchange('ks_query_start_date', 'ks_query_end_date')
    def ks_check_valid_datetime(self):
        for rec in self:
            if rec.ks_query_start_date and rec.ks_query_end_date:
                if rec.ks_query_start_date >= rec.ks_query_end_date:
                    raise ValidationError(_("Start Date should be less than End Date"))

    @api.onchange('ks_custom_query')
    def ks_empty_labels(self):
        for rec in self:
            rec.ks_xlabels = False
            rec.ks_ylabels = False

    @api.onchange('ks_is_date_ranges')
    def ks_onchange_date_ranges(self):
        for rec in self:
            rec.ks_custom_query = False

    #   function to handle the sorting for list view
    def ks_get_list_data_orderby_extend(self, domain={}):
        ks_filter_domain = domain.get('ks_domain_1', [])
        orderid = self._context.get('field', False)
        ks_field = self._context.get('field', False)
        sort_order = self._context.get('sort_order', False)
        offset = self._context.get('offset', 0)
        initial_count = self._context.get('initial_count', 0)
        ks_domain = []
        if orderid:
            orderby = self.env['ir.model.fields'].search([('id', '=', orderid)]).id
        else:
            orderby = False
        if self._context.get('ksDateFilterSelection', False):
            ks_date_filter_selection = self._context['ksDateFilterSelection']
            if ks_date_filter_selection == 'l_custom':
                self = self.with_context(
                    ksDateFilterStartDate=fields.datetime.strptime(self._context['ksDateFilterStartDate'],
                                                                   "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(
                    ksDateFilterEndDate=fields.datetime.strptime(self._context['ksDateFilterEndDate'],
                                                                 "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(ksIsDefultCustomDateFilter=False)
        else:
            ks_date_filter_selection = self.ks_dashboard_ninja_board_id.ks_date_filter_selection
            self = self.with_context(ksDateFilterStartDate=self.ks_dashboard_ninja_board_id.ks_dashboard_start_date)
            self = self.with_context(ksDateFilterEndDate=self.ks_dashboard_ninja_board_id.ks_dashboard_end_date)
            self = self.with_context(ksDateFilterSelection=ks_date_filter_selection)
        if ks_date_filter_selection not in ['l_custom', 'l_none']:
            ks_date_data = ks_get_date(ks_date_filter_selection, self, 'datetime')
            self = self.with_context(ksDateFilterStartDate=ks_date_data["selected_start_date"])
            self = self.with_context(ksDateFilterEndDate=ks_date_data["selected_end_date"])
        self = self.with_context(ksIsDefultCustomDateFilter=True)
        ks_proper_domain = self.ks_convert_into_proper_domain(self.ks_domain, self, ks_filter_domain)

        if len(ks_proper_domain) > 0:
            ks_domain = ks_domain + ks_proper_domain

        list_view_data = self.get_list_view_record(orderby, sort_order, ks_domain, ksoffset=initial_count - 1,
                                                   initial_count=initial_count)
        return list_view_data
