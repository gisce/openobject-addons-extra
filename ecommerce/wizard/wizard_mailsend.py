# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv,fields
import tools
from tools.translate import _
import base64

class ecommerce_sendmail_wizard(osv.osv_memory):
    _name = 'ecommerce.customer.sendmail'
    _rec_name = 'subject'
    _columns = {
        'partner_ids' : fields.many2many('ecommerce.partner', 'ecommerce_sendmail_rel', 'ecommerce_id', 'customer_id', 'Customer'),
        'subject' : fields.char('Subject', size=64, required=True),
        'message' : fields.text('Message', required=True),
        'attachment' : fields.many2one('ir.attachment', 'Attachment')
    }
    def mail_send(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        not_sent = []
        result = {}
        attchment_obj = self.pool.get('ir.attachment')
        mail_message = self.pool.get('mail.message')
        ecommerce_shop_rec = self.pool.get('ecommerce.shop').browse(cr, uid, context.get('active_id'), context)
        ecommerce_record = self.browse(cr, uid, ids, context=context)
        for record in ecommerce_record:
            for partner in record.partner_ids:
                if partner.id:
                    res = self.pool.get('ecommerce.partner').browse(cr, uid, partner.id)
                    if res.address_ids and not res.address_ids[0].email:
                        not_sent.append(res.name)
                    for address in res.address_ids:
                        if address.email:
                            result[res.name] = address.email
                            name = address.username or res.name
                            to = '%s <%s>' % (name, address.email)
                            mail_from = 'mansuri.sananaz@gmail.com'
                            attach_ids = attchment_obj.search(cr, uid, [('res_model', '=', 'ecommerce.shop'), ('res_id', '=', ecommerce_shop_rec.id)], context=context)
                            att_rec = attchment_obj.read(cr, uid, attach_ids, ['datas', 'datas_fname'], context=context)
                            att_rec = dict(map(lambda x: (x['datas_fname'],
                                        base64.decodestring(x['datas'])), att_rec))
                            mail_message.schedule_with_attach(cr, uid, mail_from, [to], record.subject, record.message, attachments=att_rec) 
        model_data = self.pool.get('ir.model.data')
        view_rec = model_data.get_object_reference(cr, uid, 'ecommerce', 'wizard_mailsend_finish_form_view')
        view_id = view_rec and view_rec[1] or False
        
        return {
            'name': _('Send Mail'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': 'ecommerce.sendmail.finish',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy' : True
        }
ecommerce_sendmail_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

