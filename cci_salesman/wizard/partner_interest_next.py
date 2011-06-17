# -*- coding: utf-8 -*-

from tools.translate import _

import wizard
import pooler


class partner_interest_next(wizard.interface):
    init_arch = '''<?xml version="1.0" encoding="UTF-8"?>
    <form string="Marques d'intérets">
        <separator string="Voulez-vous avancer d'un an?" />
    </form>
    '''
    
    init_fields = {}
    
    def do_next(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        
        pool = pooler.get_pool(cr.dbname)
        partner_obj = pool.get('res.partner')
        interest_obj = pool.get('res.partner.interest')
        interest_next_obj = pool.get('res.partner.interest.next')    
        
        for partner in partner_obj.browse(cr, uid, data['ids'], context):
            partner_obj.write(cr, uid, [partner.id], 
                              {'year': partner.year + 1}, context)
            for interest in partner.interest_year:
                interest_obj.unlink(cr, uid, interest.id, context)
            for interest_next in partner.interest_next_year:      
                context['next'] = True
                interest_obj.create(cr, uid, 
                    {'partner': interest_next.partner.id,
                     'date': interest_next.date,
                     'product': interest_next.product.id,
                     'cci_contact': interest_next.cci_contact.id,
                     'contact': interest_next.contact.id,
                     'category': interest_next.category.id,
                     'turnover_hoped': interest_next.turnover_hoped,
                     'next_action': interest_next.next_action,
                     'cci_contact_follow': interest_next.cci_contact_follow.id,
                     'description': interest_next.description,
                    }, context)
                interest_next_obj.unlink(cr, uid, interest_next.id, context)
            
        return {}
    
    states = {
        'init': {'actions': [],
                 'result': {'type': 'form',
                            'arch': init_arch,
                            'fields': init_fields,
                            'state': [('end', _(u'Annuler'), 'gtk-cancel'),
                                      ('ok', _(u'OK'), 'gtk-action',
                                       True)],
                           },
                },
        'ok': {'actions': [do_next],
                'result': {'type': 'state',
                           'state': 'end',
                          },
               },
    }
    
partner_interest_next('partner_interest_next')