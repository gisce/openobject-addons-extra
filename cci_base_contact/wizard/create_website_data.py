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
import random
import pooler
import tools
import os

_form = '''<?xml version="1.0"?>
<form string="Create Website Data">
    <field name="send_email"/>
    <newline/>
    <field name="from_email"/>
    <newline/>
    <field name="perso_message" colspan="4" width="650"/>
</form>'''

_fields = {
    'send_email':{'string':'Send EMail with login-password','type':'boolean','default':lambda *a: True},
    'from_email':{'string':'From','type':'char', 'size':64},
    'perso_message':{'string':'Personalized message','type':'text','help':'Not mandatory, appears at top of classical message'},
}

msg_form = """<?xml version="1.0"?>
<form string="Result">
    <field name="message" width="600" nolabel="1"/>
</form>
"""
msg_fields = {
      'message': {'string':'Result', 'type':'text','readonly':True}
      }

def _create_data(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    contact_obj = pool.get('res.partner.contact').browse(cr, uid, data['id'], context)
    newlogin = contact_obj.job_email or contact_obj.email or False
    if newlogin:
        same = pool.get('res.partner.contact').search(cr,uid,[('login_name','=',newlogin)])
        if not same:
            random.seed()
            if contact_obj.name and contact_obj.first_name:
                newpw = contact_obj.name[0:2].lower() + str(int(random.random()*1000000)).rjust(6,'0') + contact_obj.first_name[0:2].lower()
            else:
                if contact_obj.name and len(contact_obj.name) > 3:
                    newpw = contact_obj.name[0:2].lower() + str(int(random.random()*1000000)).rjust(6,'0') + contact_obj.name[2:4].lower()
                else:
                    newpw = contact_obj.name[0:2].lower() + str(int(random.random()*1000000)).rjust(6,'0') + 'am'
            if not newpw.isalpha():
                newpw = newpw.replace('.','').replace('-','.')
            same = True
            while same:
                newtoken = hex(random.getrandbits(128))[2:34]
                same = pool.get('res.partner.contact').search(cr,uid,[('token','=',newtoken)])
            res = pool.get('res.partner.contact').write(cr,uid,data['id'],{'login_name':newlogin,'password':newpw,'token':newtoken})
            if res:
                res_message = "Login-pw created '%s' / '%s' / '%s'" % (newlogin,newpw,newtoken)
                if data['form']['send_email'] and data['form']['from_email']:
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
                            text = text % (newlogin,newpw,tools.ustr(data['form']['perso_message'] or ''))
                            text = tools.ustr(text)
                            res = tools.email_send(str_from, [str_to], 'CCIConnect login et mot de passe', text )
                            if res:
                                res_message += "\nThe login-password has been send to the email address '%s'" % str_to
                            else:
                                res_message += "\nError: Mail not sent, Contact '%s %s' does not have a valid address mail : '%s' or the mail cannot be send" % (contact_obj.name, contact_obj.first_name, str_to)
            else:
                res_message = "Error while registering new login-password-token"
        else:
            res_message = 'An other contact already have the same login : ' + newlogin
    else:
        res_message = "No valid email address for this contact. Creation of login failed"
    return {'message': res_message }

class create_website_data(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_form, 'fields': _fields, 'state':[('create','Create login and Send mail'),('end','Cancel')]}
        },
        'create': {
            'actions': [_create_data],
            'result': {'type':'form', 'arch': msg_form, 'fields': msg_fields, 'state':[('end','Ok')]}
        },
    }
create_website_data('cci_base_contact.create_website_data')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

