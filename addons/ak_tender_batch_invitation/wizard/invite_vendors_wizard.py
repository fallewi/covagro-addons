# -*- coding: utf-8 -*-
from odoo import models, fields, _


class InviteVendorsWizard(models.TransientModel):
    _name = 'invite.vendors.wizard'
    _description = 'Créer des appels d\'offres par lots'

    error_message = 'Aucun fournisseur trouvé pour cet agrément.'

    def get_requisition_lines(self, requisition_id):
        lines_list = []
        for line in requisition_id.line_ids:
            lines_list.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.price_unit,
                # 'date_planned': line.schedule_date or fields.Date.today(),
            }))
        return lines_list

    def display_notification(self,title, message, type):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': type,
                'sticky': False,
                'next':  {'type': 'ir.actions.act_window_close'},
            }
        }

    def create_rfq_for_vendor(self, partner_line, requisition_id):
        purchase_order_id = self.env['purchase.order'].create({
            'partner_id': partner_line.partner_id.id,
            'requisition_id': requisition_id.id,
            'origin': requisition_id.name,
            'notes': requisition_id.description,
            'date_order': requisition_id.schedule_date or fields.Date.today(),
            'date_planned': requisition_id.schedule_date or fields.Date.today(),
            'order_line': self.get_requisition_lines(requisition_id)
        })
        return purchase_order_id

    def send_rfq_email(self, partner_id, purchase_order_id):
        if partner_id.email:
            template = self.env.ref('purchase.email_template_edi_purchase')
            template.send_mail(purchase_order_id.id, force_send=False)
            purchase_order_id.state = 'sent'
            return True
        else:
            return False

    def action_create_rfq_with_email(self):
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and udpate partner line:
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                # send the email to vendor:
                email_sent = self.send_rfq_email(partner_line.partner_id, purchase_order_id)
                if email_sent:
                    partner_line.invitation_state = 'sent_with_email'
                else:
                    partner_line.invitation_state = 'sent'
        if new_vendors_count > 0:
            return self.display_notification('Invitations Envoyées', f'{new_vendors_count} nouveaux appels d\'offre crées.', 'success') 
        else:
            if len(requisition_id.partner_ids) == 0:
                return self.display_notification('Pas de fournisseurs', 'Veuillez ajouter des fournisseurs à partir de l\'onglet "Fournisseurs" et réessayer.', 'danger')
            else:
                return self.display_notification('Aucun appel d\'offre crée', 'Aucun nouveau fournisseur trouvé', 'danger')

    def action_create_rfq_only(self):
        new_vendors_count = 0
        requisition_id = self.env['purchase.requisition'].browse(self._context.get('active_id'))
        for partner_line in requisition_id.partner_ids:
            if partner_line.invitation_state == 'new':
                new_vendors_count += 1
                # create the RFQ and udpate partner line:
                purchase_order_id = self.create_rfq_for_vendor(partner_line, requisition_id)
                partner_line.purchase_order_id = purchase_order_id.id
                partner_line.invitation_state = 'sent'
        if new_vendors_count > 0:
            return self.display_notification('Appel d\'offre crée', f'{new_vendors_count} new RFQ(s) created.', 'success')
        else:
            if len(requisition_id.partner_ids) == 0:
                return self.display_notification('Pas de Fournisseurs', 'Veuillez ajouter des fournisseurs à partir de l\'onglet "Fournisseurs" et réessayer.', 'danger')
            else:
                return self.display_notification('Aucun appel d\'offre crée', 'Pas de Fournisseurs trouvé', 'danger')


