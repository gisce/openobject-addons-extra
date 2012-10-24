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

class wizard_ecommerce_sendmail_finish(osv.osv_memory):
    _name = 'ecommerce.sendmail.finish'
    _rec_name = 'mailsent'
    _columns = {
        'mailsent' : fields.text('Mail Sent To'),
        'mailnotsent' : fields.text('Mail Not sent'),
    }
    
    def get_mail_detail(self, cr, uid, ids, context=None):
        sent_dict = {}
        result = []
        not_sent = []
        sent = []
        mail_value = ''
        not_mail = ''
        ecommerce_sendmail_data = self.pool.get('ecommerce.customer.sendmail').browse(cr, uid, ids, context=context)
        for record in ecommerce_sendmail_data:
            for partner in record.partner_ids:
                res = self.pool.get('ecommerce.partner').browse(cr, uid, partner.id)
                if res.address_ids and not res.address_ids[0].email:
                    not_sent.append(res.name)
                for address in res.address_ids:
                    if address.email:
                        sent_dict[res.name] = address.email
                    for items in sent_dict:
                        result.append(items) 
                        mail_value = mail_value + ',' + items
                    for items_not in not_sent:
                        sent.append(items_not)
                        not_mail = not_mail + ',' + items_not
        return {'mailsent': str(mail_value), 'mailnotsent': str(not_mail)}
wizard_ecommerce_sendmail_finish()