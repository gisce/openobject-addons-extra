# -*- coding: utf-8 -*-

from tools.translate import _

import wizard
import pooler


class partner_interest_order(wizard.interface):
    
    init_fields = {}
    
    def do_order(self, cr, uid, data, context=None):
        if context is None:
            context = {}
            
        pool = pooler.get_pool(cr.dbname)
        model = False
        res_id = False
        
        if data['model'] == 'res.partner.interest':
            interest_obj = pool.get('res.partner.interest')
        else:
            interest_obj = pool.get('res.partner.interest.next')
        
        interest = interest_obj.browse(cr, uid, data['id'])

        if interest.product and interest.product.order_type and \
            interest.partner:
            if interest.product.order_type == 'participation' and \
                interest.contact:
                model = 'cci_club.participation'
                participation_obj = pool.get('cci_club.participation')
                participation_state_obj = \
                    pool.get('cci_club.participation_state')
                    
                state = participation_state_obj.search(cr, uid, 
                                    [('name', '=', 'EN ATTENTE DE GROUPE')])[0]
                
                values  = {'partner_id': interest.partner.id,
                           'contact_id': interest.contact.contact_id.id,
                           'provided_turnover': interest.turnover_hoped,
                           'state_id': state,
                           'salesman': interest.partner.user_id.id}
                
                res_id = participation_obj.create(cr, uid, values)

                values = participation_obj.onchange_partner(cr, uid, [res_id], 
                                                interest.partner.id, False,
                                                interest.contact.contact_id.id)
                participation_obj.write(cr, uid, [res_id], values['value'])
                
            elif interest.product.order_type == 'order' and \
                interest.category and interest.category.product:
                model = 'sale.order'
                order_obj = pool.get('sale.order')
                order_line_obj = pool.get('sale.order.line')
                
                values  = {'partner_id': interest.partner.id}
                values.update(order_obj.onchange_partner_id(cr, uid, 
                                    False, interest.partner.id)['value'])
                res_id = order_obj.create(cr, uid, values)
                
                values = order_line_obj.product_id_change(cr, uid, False, 
                                    False, interest.category.product.id, qty=1, 
                                    partner_id=interest.partner.id)['value']
                                    
                values.update({'order_id': res_id,
                               'product_id': interest.category.product.id,
                               'price_unit': interest.turnover_hoped})
                order_line_obj.create(cr, uid, values)

            elif interest.product.order_type == 'membership':
                model = 'res.partner'
                partner_obj = pool.get('res.partner')
            else:
                raise wizard.except_wizard(('Erreur !'),
                ('Des données sont manquantes.'))
                
            interest_obj.write(cr, uid, [data['id']], {'turnover_hoped': 0})
        
        value = {}
        
        if model and res_id:
            value = {
                'domain': "[]",
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': model,
                'res_id': [res_id],
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
            
        return value
    
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': do_order, 'state': 'end'}
        }
    }
    
partner_interest_order('partner_interest_order')