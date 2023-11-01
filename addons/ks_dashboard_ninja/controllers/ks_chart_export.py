
import re
import datetime
import io
import json
import operator

from odoo.addons.web.controllers.main import ExportFormat,serialize_exception, ExportXlsxWriter
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from odoo.tools import pycompat


class KsChartExport(http.Controller):

    def base(self, data):
        params = json.loads(data)
        header,chart_data = operator.itemgetter('header','chart_data')(params)
        chart_data = json.loads(chart_data)
        chart_data['labels'].insert(0,'Measure')
        columns_headers = chart_data['labels']
        import_data = []

        for dataset in chart_data['datasets']:
            dataset['data'].insert(0, dataset['label'])
            import_data.append(dataset['data'])

        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(header))),
                     ('Content-Type', self.content_type)],
            # cookies={'fileToken': token}
                                     )




class KsChartExcelExport(KsChartExport, http.Controller):

    # Excel needs raw data to correctly handle numbers and date values
    raw_data = True

    @http.route('/ks_dashboard_ninja/export/chart_xls', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        return self.base(data)

    @property
    def content_type(self):
        return 'application/vnd.ms-excel'

    def filename(self, base):
        return base + '.xls'

    def from_data(self, fields, rows):
        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value


class KsChartCsvExport(KsChartExport, http.Controller):

    @http.route('/ks_dashboard_ninja/export/chart_csv', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        return self.base(data)

    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def filename(self, base):
        return base + '.csv'

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str)    and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()
