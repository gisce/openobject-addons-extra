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
import tools
import os

_form = '''<?xml version="1.0"?>
<form string="Print Partner Data">
    <field name="template colspan="4"/>
</form>'''

_fields = {
    'template': {'string':'Template',
               'type':'selection',
               'selection':[('commercial',"Prioritaire dans une autre CCI"),
                            ('interne',u"Ne désire plus être abonné"),
                           ],
               'default': lambda *a: 'commercial',
              },
}

def _send_data(self, cr, uid, data, context):
    text = u'''Suite à votre demande, voici votre login et votre mot de passe pour vous connecter sur le site de la CCI Connect : www.cciconnect.be.

Login : %s

Mot de passe : %s

%s

Bienvenue.'''

    str_to = 'test@cciconnect.be'
    str_from = ''
    pool = pooler.get_pool(cr.dbname)
    contact_obj = pool.get('res.partner.contact').browse(cr, uid, data['id'], context)
    str_from = data['form']['from_email'] or 'nepasrepondre@cciconnect.be'  ## the field is required, this not usefull
    str_to = contact_obj.job_email or contact_obj.email or str_to
    #TODO check email address from
    if str_to and str_from:
        if contact_obj.login_name and not contact_obj.login_name in ['jamais','autrezone','double_email']:
            text = text % (contact_obj.login_name,contact_obj.password,tools.ustr(data['form']['perso_message'] or ''))
            text = tools.ustr(text)
            res = tools.email_send(str_from, [str_to], 'CCIConnect login et mot de passe', text )
            if res:
                res_message = "The login-password has been resend to the email address '%s'" % str_to
            else:
                res_message = "Error: Mail not sent, Contact '%s %s' does not have a valid address mail : '%s' or the mail cannot be send" % (contact_obj.name, contact_obj.first_name, str_to)
        else:
            res_message = "Error: Contact '%s %s' has no valid login_name : '%s'" % (contact_obj.name, contact_obj.first_name, contact_obj.login_name )
    return {'message': res_message }

class print_partner_data(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_form, 'fields': _fields, 'state':[('print','Print'),('end','Cancel')]}
        },
        'send': {
            'actions': [_send_data],
            'result': {'type':'form', 'arch': msg_form, 'fields': msg_fields, 'state':[('end','Ok')]}
        },
    }
print_partner_data('cci_last_module.print_partner_data')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

