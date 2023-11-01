# See LICENSE file for full copyright and licensing details.
"""Contact Team Trip Ticket."""


from odoo import models


class ContactTeamTrip(models.AbstractModel):
    """Contact Team Trip Model."""

    _name = 'report.fleet_operations.contact.team.trip.ticket.xls'
    _description = 'Contacter l\'équipe Rapport de billet de voyage'

    def get_heading(self):
        """Report print method."""
        head_title = {'name': '',
                      'rev_no': '',
                      'doc_no': '',
                      }
        head_object = self.env['report.heading']
        head_ids = head_object.search([], order='id')
        if head_ids:
            head_rec = head_ids[0]
            if head_rec:
                head_title['name'] = head_rec.name or ''
                head_title['rev_no'] = head_rec.revision_no or ''
                head_title['doc_no'] = head_rec.document_no or ''
                head_title['image'] = head_rec.image or ''
        return head_title

    def generate_xlsx_report(self, workbook, data, trip_ticket):
        """Report format Excel."""
        worksheet = workbook.add_worksheet('contact_team_trip_ticket')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 10)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 20)
        worksheet.set_column(13, 13, 5)
        worksheet.set_column(14, 14, 5)
        worksheet.set_column(15, 15, 5)

        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        worksheet.merge_range('C3:F3', 'Merged Cells', merge_format)

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'CONTACTER L\'ÉQUIPE BILLET DE VOYAGE', tot)
        row = 1
        for obj in trip_ticket:
            row += 3
            worksheet.write(row, 0, 'Coordonnées de l\'équipe :', bold)
            worksheet.write(row, 9, 'ID de voyage :', bold)
            worksheet.write(row, 10, obj.id or '')
            row += 1
            worksheet.write(row, 0, 'Nom de l\'équipe de contact :', bold)
            worksheet.write(row, 3, obj.destination_location_id and
                            obj.destination_location_id.name or '')
            worksheet.write(row, 9, 'Date du voyage :', bold)
            worksheet.write(row, 10, obj.trip_date or '')
            row += 1
            worksheet.write(row, 0, 'Destination :', bold)
            worksheet.write(row, 3, obj.location_id or '')
            worksheet.write(row, 9, 'Date de retour :', bold)
            worksheet.write(row, 10, obj.return_date or '')
            row += 1
            worksheet.write(row, 9, 'Statut :', bold)
            worksheet.write(row, 10, obj.state or '')
            row += 1
            worksheet.write(row, 0, 'Pièces incluses :', bold)
            row += 2
            worksheet.write(row, 0, 'No.', format1)
            worksheet.write(row, 1, 'Numéro de pièce.', format1)
            worksheet.write(row, 2, 'Nom de la pièce', format1)
            worksheet.write(row, 3, 'Marque du véhicule', format1)
            worksheet.write(row, 4, 'Type d\'unité', format1)
            worksheet.write(row, 5, 'Qté. sur Camion', format1)
            worksheet.write(row, 6, 'Utilisé', format1)
            worksheet.write(row, 7, 'Manquant', format1)
            worksheet.write(row, 8, 'Endommagé', format1)
            worksheet.write(row, 9, 'Restant', format1)
            worksheet.write(row, 10, 'Réapprovisionnement', format1)
            worksheet.write(row, 11, 'Nouvelle quantité.', format1)
            worksheet.write(row, 12, 'Remarques', format1)
            line_row = row + 1
            line_col = 0
            counter = 1
            if obj.allocate_part_ids:
                for line in obj.allocate_part_ids:
                    worksheet.write(line_row, line_col, counter, border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    line.product_id and
                                    line.product_id.default_code or '', border)
                    line_col += 1
                    worksheet.write(line_row, line_col, line.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    line.vehicle_make_id and
                                    line.vehicle_make_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    line.product_id.uom_id and
                                    line.product_id.uom_id.name or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    line.qty_on_truck or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, line.qty_used or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, line.qty_missing or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, line.qty_damage or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col,
                                    line.qty_remaining or '',
                                    border)
                    line_col += 1
                    worksheet.write(line_row, line_col, None, border)
                    line_col += 1
                    worksheet.write(line_row, line_col, None, border)
                    line_col += 1
                    worksheet.write(line_row, line_col, line.remark or '',
                                    border)
                    line_col = 0
                    line_row += 1
                    counter += 1
                    worksheet.write(line_row, line_col, '********', border)
            row += 5
            worksheet.write(row, 0, 'Mécanique:', bold)
            worksheet.write(row, 9, 'Notes:', bold)
            worksheet.write(row, 10, obj.note or '')
            row += 1
            worksheet.write(row, 0, 'Préparé par:', bold)
            worksheet.write(row, 1, obj.prepairdby_id and
                            obj.prepairdby_id.name or '')
            row += 2
