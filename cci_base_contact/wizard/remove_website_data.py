# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

import wizard
import netsvc
import wizard
import netsvc
import pooler
import os

_form = '''<?xml version="1.0"?>
<form string="Remove Website Data">
    <field name="reason" colspan="4"/>
</form>'''

_fields = {
    'reason': {'string':'Reason',
               'type':'selection',
               'selection':[('autrezone',"Prioritaire dans une autre CCI"),
                            ('jamais',u"Ne désire plus être abonné"),
                            ('double_email',u"Cette adresse email existe sur une autre fiche, en double"),
                            ('erase',u"Simple effacement (si membre, sera réabonné)")],
               'default': lambda *a: 'jamais',
              },
}

def _remove_data(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    obj_contact = pool.get('res.partner.contact')

    newlogin = data['form']['reason']
    if data['form']['reason'] == 'erase':
        newlogin = ''
    obj_contact.write(cr, uid, data['ids'], {'login_name':newlogin,'token':'','password':''} )
    return {}

class remove_website_data(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_form, 'fields': _fields, 'state':[('remove','Erase Data'),('end','Cancel')]}
        },
        'remove': {
            'actions': [_remove_data],
            'result': {'type':'state','state':'end'}
        },
    }
remove_website_data('cci_base_contact.remove_website_data')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

