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
# version 2.0 : don't create a false ata cranet to simulate, compute directly
import wizard
import netsvc
import pooler
import time

from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Compute ATA Carnet Price">
    <separator string="Warranty"/>
</form>"""
fields = {}

param_form = """<?xml version="1.0"?>
<form string="Compute ATA Carnet Price">
    <field name="creation_date"/>
    <newline/>
    <field name="type"/>
    <newline/>
    <field name="goods_value"/>
    <newline/>
    <field name="double_signature"/>
    <newline/>
    <field name="member_price"/>
    <newline/>
    <field name="pages"/>
    <newline/>
    <separator string="Warranty" colspan="4"/>
    <field name="own_risk"/>
    <newline/>
    <field name="manual_warranty"/>
</form>"""

param_fields = {
    'type': {'string':'Type','type': 'many2one', 'relation': 'cci_missions.dossier_type', 'domain':"[('section','=','ATA')]",'required': True},
    'creation_date': {'string' : 'Creation Date', 'type':'date','required': True,'default' : lambda *a: time.strftime('%Y-%m-%d') },
    'goods_value': {'string' : 'Goods Value', 'type':'float','size' : (10,2),'required': True},
    'double_signature': {'string' : 'Double signature', 'type' : 'boolean', 'default' : lambda *a: True }, 
    'member_price': {'string': 'Member price', 'type':'boolean', 'help':'Do we apply member price for the concerned partner ?'},
    'pages': {'string':'Number of pages','type':'integer'},
    'own_risk': {'string':'Own risk','type':'boolean','help':'If not own risk, apply the standard warranty'},
    'manual_warranty': {'string':'Manual warranty','type':'float','help':'Used only if own risk to give the current warranty claimed to the customer'},
   }

msg_form = """<?xml version="1.0"?>
<form string="Simulation">
    <field name="msg" width="400" nolabel="1"/>
</form>
"""

msg_fields = {
        'msg': {'string':'Total Amount to Pay', 'type':'text', 'readonly':True},
         }

def _compute_price(self, cr, uid, data, context):
    print data
    pool_obj = pooler.get_pool(cr.dbname)
    obj_dossiertype = pool_obj.get('cci_missions.dossier_type')
    dossier_type = obj_dossiertype.browse(cr,uid,data['form']['type'])
    obj_lines=pool_obj.get('account.invoice.line')
    #context.update({'pricelist': carnet.partner_id.property_product_pricelist.id})
    prod_list = []
    value = []
    prod_list.append(dossier_type.original_product_id.id)
    prod_list.append(dossier_type.copy_product_id.id)
    if data['form']['own_risk']:
        prod_list.append(dossier_type.warranty_product_1.id)
    else:
        prod_list.append(dossier_type.warranty_product_2.id)
    print prod_list
    context.update({'date':data['form']['creation_date']})
    count=0
    qty_copy=data['form']['pages']
    if qty_copy<0:
       qty_copy=0
    force_member=force_non_member=False
    if data['form']['member_price']:
        force_member=True
        ptype = 'member_price'
    else:
        force_non_member=True
        ptype = 'list_price'
    context.update({'partner_id':False})
    context.update({'force_member':force_member})
    context.update({'force_non_member':force_non_member})
    context.update({'value_goods':data['form']['goods_value']})
    context.update({'double_signature':data['form']['double_signature']})
    context.update({'date':data['form']['creation_date']})
    context.update({'emission_date':data['form']['creation_date']})

    for prod_id in prod_list:
        count +=1
        price=pool_obj.get('product.product').price_get(cr, uid, [prod_id], ptype, context)
        value.append(price[prod_id])
    sum = value[0]+round(value[1]*qty_copy,2)
    if data['form']['own_risk']:
        sum += data['form']['manual_warranty']
    else:
        sum += value[2]
    message_total = """The final price will be %10.2f euros.
Don't forget to mention addititional products (like postal costs).""" % (sum)
    return {'msg' : message_total}

class compute_ata_price(wizard.interface):

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':param_form, 'fields':param_fields, 'state':[('end','Cancel'),('compute','Compute')]},
        },
        'compute': {
            'actions': [_compute_price],
            'result': {'type':'form', 'arch':msg_form, 'fields':msg_fields, 'state':[('end','Ok')]}
        },
    }

compute_ata_price("mission.simulation_carnet")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

