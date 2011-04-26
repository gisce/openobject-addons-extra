# -*- coding: utf-8 -*-
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
import datetime

from osv import fields
import wizard
import pooler
from tools.translate import _

_final_fields = {
    'final_text': {'string':'Changes', 'type':'char','readonly':True,'value':'-','size':10000},
    'final_count' : {'string':'Count','type':'integer','readonly':True,'value':-1}
}
def _valid_membership(self, cr, uid, data, context):
    # this method is partially copied in the method cci_membership=>cci_membership.py=>_membership_state_job()
    partner_ids = data['ids']
    partner_obj = pooler.get_pool(cr.dbname).get('res.partner')
    if partner_ids:
        partners = partner_obj.read(cr, uid, partner_ids, ['id','membership_state'] )
        new_mstates = partner_obj._membership_state(cr, uid, partner_ids, '', args=None, context=None)
        changed_lines = []
        for partner in partners:
            if new_mstates.has_key( partner['id'] ):
                if partner['membership_state'] <> new_mstates[partner['id']]:
                    partner_name = partner_obj.read(cr, uid, [partner['id']], ['name'] )[0]['name']
                    changed_lines.append( u"Partenaire '%s' (id=%s) passe de '%s' à '%s'" % (partner_name, str(partner['id']),partner['membership_state'],new_mstates[partner['id']]) )
                    partner_obj.write(cr, uid, [partner['id']], {}, context )
        if changed_lines:
            final_text = u'Changements manuels : \n' + ( u'\n'.join( changed_lines ) )
        else:
            final_text = u"Changements manuels : aucun"
        membership_check = pooler.get_pool(cr.dbname).get('cci_membership.membership_check')
        today = datetime.datetime.today()
        id = membership_check.create(cr, uid, {
            'name': today.strftime('%Y-%m-%d-%H:%M:%S'),
            'count' : len(changed_lines),
            'status': final_text,
            })
        _final_fields['final_text']['value'] = final_text
        _final_fields['final_count']['value'] = len(changed_lines)
    return {'type':'state','state':'show'}

#wizard_arch= """<?xml version="1.0"?>
#<form string="Check Membership State of all Partners">
#    <label string="This wizard will check the membership state of all partners ..." colspan="4"/>
#    <label string="This check can be very long if you have a lot of partners."/>
#</form>"""

_wizard_final_arch = """<?xml version="1.0"?>
<form string="Changes">
    <separator string="------ Result of the re-calculation of the membership state -----" colspan="4"/>
    <field name="final_text" colspan="4" nolabel="1"/>
    <field name="final_count"/>
</form>"""

class cci_wizard_valid_membership(wizard.interface):

    states = {
        'init' : {
            'actions' : [_valid_membership],
            'result' : {
                'type' : 'state',
                'state' : 'show'}
        },
        'show' : {
            'actions' : [],
            'result' : {
                'type' : 'form',
                'arch' : _wizard_final_arch,
                'fields' : _final_fields,
                'state' : [('end','Close')]}
        },
    }
cci_wizard_valid_membership("cci_wizard_valid_membership")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
