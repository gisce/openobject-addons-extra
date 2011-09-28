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
import wizard
import pooler
import time
import datetime

form = """<?xml version="1.0"?>
<form string="Selecting Invoices" colspan="4">
    <field name="year"/>
    <field name="select"/>
</form>
"""

fields = {
    'year':{'string':'Year of membership','type':'integer','required':True},
    'select':{'string':'Type of invoice','type':'selection','selection':[('all','Invoices and Refunds'),('invoice','Invoices only'),('refund','Refunds only')]},
}


class select_invoices_by_year(wizard.interface):

    def _defaults(self, cr, uid, data, context):
        data['form']['year'] = datetime.datetime.today().year
        data['form']['select'] = 'invoice'
        return data['form']

    def _open_window_selected_invoices(self, cr, uid, data, context):
        if data['form']['year'] < 1900 or data['form']['year'] > datetime.datetime.today().year + 2:
            raise wizard.except_wizard('Warning','You must give the year of membership searched; between 1900 and the next year')

        #mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        #act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')
        #result = mod_obj._get_id(cr, uid, 'account', 'invoice_tree')
        #id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        #result = act_obj.read(cr, uid, [id])[0]

        #print result

        if data['form']['select'] == 'refund':
            sel_types = " = 'out_refund'"
        elif  data['form']['select'] == 'invoice':
            sel_types = " = 'out_invoice'"
        else:
            sel_types = " in ('out_invoice','out_refund')"
        selection = "select distinct(ainv.id) from account_invoice as ainv, account_invoice_line as ail, product_product as pp where pp.membership and pp.membership_year = " + str(data['form']['year']) + " and ail.product_id = pp.id and ainv.id = ail.invoice_id and ainv.type " + sel_types
        cr.execute( selection )
        result_lines = cr.fetchall()
        inv_ids = [x[0] for x in result_lines]
        #print inv_ids
        #result['domain'] = [('id', 'in', inv_ids)]
        result = {
            'domain': [('id', 'in', inv_ids)],
            'name': 'Membership Invoices of ' + str(data['form']['year']),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'context': { },
            'type': 'ir.actions.act_window'
        }
        return result

    states = {
        'init' : {
            'actions' : [_defaults],
            'result' : {'type' : 'form' , 'arch' : form,
                    'fields' : fields,
                    'state' : [('end', 'Cancel'), ('go', 'Go')]}
        },
        'go': {
            'actions': [],
            'result': {'type': 'action', 'action':_open_window_selected_invoices, 'state':'end'}
        }

    }
select_invoices_by_year("select_invoices_by_year")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

