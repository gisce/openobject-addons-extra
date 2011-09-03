# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
# Version 1.0 Philmer
import wizard
import time
import datetime
#import re
import tools
import pooler
import base64
from pyExcelerator import *

form = """<?xml version="1.0"?>
<form string="Options">
    <field name="choice" colspan="4"/>
</form>"""

fields = {
    'choice': {'string': 'Selection', 'type':'selection','selection': [('all','Toutes les inscriptions'),('selected','Seulement les actives')],'required': True,'default':'all'},
   }

msg_form = """<?xml version="1.0"?>
<form string="Notification">
     <separator string="File has been created."  colspan="4"/>
     <field name="msg" colspan="4" nolabel="1"/>
     <field name="inscriptions" colspan="4" />
</form>"""

msg_fields = {
    'msg': {'string':'File created', 'type':'text', 'size':'100','readonly':True},
    'inscriptions':{'string': 'Prepared file',
        'type': 'binary',
        'readonly': True,},
}

class wizard_extract_reg(wizard.interface):
    def _get_file(self,cr,uid,data,context):
        obj_registration = pooler.get_pool(cr.dbname).get('event.registration')
        if data['form']['choice'] == 'all':
            reg_ids = obj_registration.search(cr,uid,[('event_id','in',data['ids'])])
        else:
            reg_ids = obj_registration.search(cr,uid,[('event_id','in',data['ids']),('state','in',['open','done'])])
        if reg_ids:
            registrations = obj_registration.browse(cr,uid,reg_ids)
        else:
            registrations = []

        wb1 = Workbook()
        ws1 = wb1.add_sheet('Inscriptions')
        ws1.write(0,0,'event_id')
        ws1.write(0,1,'registration_id')
        ws1.write(0,2,'partner_id')
        ws1.write(0,3,'partner_invoice_id')
        ws1.write(0,4,'contact_id')
        ws1.write(0,5,'event_name')
        ws1.write(0,6,'badge_name')
        ws1.write(0,7,'badge_title')
        ws1.write(0,8,'badge_partner')
        ws1.write(0,9,'registration_state')
        ws1.write(0,10,'contact_name')
        ws1.write(0,11,'contact_first_name')
        ws1.write(0,12,'email')
        ws1.write(0,13,'courtesy')
        ws1.write(0,14,'partner_name')
        ws1.write(0,15,'partner_membership_state')
        ws1.write(0,16,'unit_price')
        ws1.write(0,17,'nb_register')
        ws1.write(0,18,'ask_attest')
        ws1.write(0,19,'cavalier')
        ws1.write(0,20,'comments')
        ws1.write(0,21,'group_name')
        ws1.write(0,22,'invoice_number')
        line = 1
        for reg in registrations:
            ws1.write(line,0,reg.event_id.id)
            ws1.write(line,1,reg.id)
            ws1.write(line,2,reg.partner_id.id)
            ws1.write(line,3,reg.partner_invoice_id.id)
            ws1.write(line,4,reg.contact_id.id)
            ws1.write(line,5,reg.event_id.name)
            ws1.write(line,6,reg.badge_name or '')
            ws1.write(line,7,reg.badge_title or '')
            ws1.write(line,8,reg.badge_partner or '')
            ws1.write(line,9,reg.state or '')
            ws1.write(line,10,reg.contact_id.name or '' )
            ws1.write(line,11,reg.contact_id.first_name or '' )
            ws1.write(line,12,reg.email_from or '' )
            ws1.write(line,13,reg.contact_id.title or '' )
            ws1.write(line,14,reg.partner_id.name or '')
            ws1.write(line,15,reg.partner_id.membership_state or '')
            ws1.write(line,16,reg.unit_price or 0.0 )
            ws1.write(line,17,reg.nb_register or '' )
            ws1.write(line,18,reg.ask_attest and 'Oui' or 'Non')
            ws1.write(line,19,reg.cavalier and 'Oui' or 'Non')
            ws1.write(line,20,reg.comments or '')
            ws1.write(line,21,reg.group_id and reg.group_id.name or '' )
            ws1.write(line,22,reg.invoice_id and reg_invoice_id.number or '' )
            line += 1
        wb1.save('registrations.xls')
        result_file = open('registrations.xls','rb').read()

        # give the result tos the user
        data['form']['msg']='Save the File with '".xls"' extension.'
        data['form']['inscriptions']=base64.encodestring(result_file)
        return data['form']

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('getfile','Get Excel File')]},
        },
        'getfile': {
            'actions': [_get_file],
            'result': {'type':'form', 'arch':msg_form, 'fields':msg_fields, 'state':[('end','Ok')]}
        },
    }

wizard_extract_reg('cci_event.extract_registrations')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

