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
    <field name="choice" colspan="4" width="500"/>
</form>"""

fields = {
    'choice': {'string': 'Selection', 'type':'selection','selection': [('all','Devis et bons de commande'),('selected','Seulement les bons de commande confirmés')],'required': True,'default':'all'},
   }

msg_form = """<?xml version="1.0"?>
<form string="Notification">
     <separator string="File has been created."  colspan="4"/>
     <field name="msg" colspan="4" nolabel="1"/>
     <field name="proofs" colspan="4" />
</form>"""

msg_fields = {
    'msg': {'string':'File created', 'type':'text', 'size':'100','readonly':True},
    'proofs':{'string': 'Prepared file',
        'type': 'binary',
        'readonly': True,},
}

class wizard_extract_proof(wizard.interface):
    def _get_file(self,cr,uid,data,context):
        proofs = []
        obj_sol = pooler.get_pool(cr.dbname).get('sale.order.line')
        sol_ids = obj_sol.search(cr,uid,[('adv_issue','in',data['ids'])] )
        if sol_ids:
            sales_lines = obj_sol.read(cr,uid,sol_ids,['order_id'])
            so_ids = []
            for sol in sales_lines:
                so_ids.append(sol['order_id'][0])
            if so_ids:
                obj_so = pooler.get_pool(cr.dbname).get('sale.order')
                if data['form']['choice'] == 'all':
                    states = ['manual','progress','draft']
                else:
                    states = ['manual','progress']
                selected_so_ids = obj_sol.search(cr,uid,[('state','in',states),('id','in',so_ids)] )
                if selected_so_ids:
                    obj_proof = pooler.get_pool(cr.dbname).get('sale.advertising.proof')
                    proof_ids = obj_proof.search(cr,uid,[('target_id','in',selected_so_ids)])
                    if proof_ids:
                        proofs = obj_proof.browse(cr,uid,proof_ids)
        wb1 = Workbook()
        ws1 = wb1.add_sheet('Preuves de parution')
        ws1.write(0,0,'contact')
        ws1.write(0,1,'company_name')
        ws1.write(0,2,'street')
        ws1.write(0,3,'street2')
        ws1.write(0,4,'zip_code')
        ws1.write(0,5,'zip_loc')
        ws1.write(0,6,'order_name')
        ws1.write(0,7,'order_state')
        line = 1
        if proofs:
            for proof in proofs:
                count = proof.number or 1
                for i in range(0,count):
                    ws1.write(line,0,proof.name or '')
                    ws1.write(line,1,proof.target_id.partner_id.name or '')
                    ws1.write(line,2,proof.address_id.street or '')
                    ws1.write(line,3,proof.address_id.street2 or '')
                    ws1.write(line,4,proof.address_id.zip_id.name or '')
                    ws1.write(line,5,proof.address_id.zip_id.city or '')
                    ws1.write(line,6,proof.target_id.name or '')
                    ws1.write(line,7,proof.target_id.state or '')
                    line += 1
            data['form']['msg']='Save the File with '".xls"' extension.'
        else:
            data['form']['msg']='No proofs found for this issue.'
        wb1.save('proofs.xls')
        result_file = open('proofs.xls','rb').read()

        # give the result to the user
        data['form']['proofs']=base64.encodestring(result_file)
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

wizard_extract_proof('cci_sales.extract_proofs')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

