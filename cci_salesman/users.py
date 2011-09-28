# -*- coding: utf-8 -*-

from osv import osv
from osv import fields
from datetime import date


class res_users(osv.osv):
    _inherit = 'res.users'
    
    def _get_year(self,cr,uid,context):
        today = date.today()
        currentYear = today.strftime("%Y")
        yearTab = []
        
        for i in xrange(int(currentYear) + 2, int(currentYear) - 2, -1):
            yearTab.append((str(i), str(i)))

        return tuple(yearTab)
    
    def _get_commission(self,cr, uid, ids, year, context):
        res= {}
        #effacement de la table
        commission_obj = self.pool.get('res.commission')
        all_com_ids = commission_obj.search(cr, uid, [])
        commission_obj.unlink(cr, uid, all_com_ids)

        ## prendre tout les product_obj commissionne
        cci_product_obj = self.pool.get('cci.product')
        cci_product_ids = cci_product_obj.search(cr, uid, [('commissioned', '=', True)])
        
        lines = []
        real_tot = obj_tot = com1_tot = com2_tot = 0

        #if view tree
        if  len(ids) != 1: 
            return res

        commissions = []
        for cci_id in cci_product_ids:
            objective = com1 = com2 = 0

            #calcul du realise
            cr.execute("""
                SELECT SUM(ail.price_subtotal) as amount
                FROM account_invoice_line ail,
                    account_invoice ai,
                    cci_product_category cpc,
                    cci_product cp
                WHERE ail.invoice_id = ai.id
                    AND ail.product_id = cpc.product
                    AND cpc.cci_product = cp.id
                    AND cp.commissioned is true
                    AND ai.user_id = %d
                    AND cp.id = %d
                    AND date_part('year', ai.date_invoice) = %d
                """ % (ids[0], cci_id, int(year)))
            lines = cr.fetchall()

            if None in lines[0]:
                del lines[0]

            realised = 0
            if len(lines) > 0:  
                realised = int(lines[0][0] or 0)
                
            #find objective
            objective_obj = self.pool.get('cci.objectif')
            obj_id = objective_obj.search(cr, uid, [('user', '=', ids[0]),
                                                    ('year', '=', year),
                                                    ('cci_product', '=', cci_id)])
            if len(obj_id) == 1:
                objective = objective_obj.browse(cr, uid, obj_id, context)[0]['objective']
                obj_id = obj_id[0]
            else:
                data_objectif = {'user': ids[0],
                        'year': year,
                        'cci_product': cci_id,
                        'objective' : 0}
                obj_id = objective_obj.create(cr, uid, data_objectif, context) 
            
            #calcul des totaux et des com
            real_tot += realised
            obj_tot += objective
            
            if realised < objective:
                com1 = realised * 0.015
                com1_tot += realised * 0.015
            else: 
                com2 = realised * 0.025
                com2_tot += realised * 0.025
            
            data = {'product': cci_id,
                    'realised': realised,
                    'objectif': objective,
                    'objective_id': obj_id,
                    'com1' : com1,
                    'com2' : com2,
                    }
            context['read'] = True
            id = commission_obj.create(cr, uid, data, context)

            commissions.append(int(id))
            
        res.update({'commission': commissions,
                    'realised_total': real_tot,
                    'objective_total': obj_tot,
                    'com1_total': com1_tot,
                    'com2_total': com2_tot
                  })

        return res
    
    def onchange_year(self, cr, uid, ids, years, context=None):
        if context is None:
            context = {}
        return {'value':self._get_commission(cr, uid, ids, years, context)}
    
    def read(self, cr, uid, ids, fields, context=None, load='_classic_read'):
        res = {}
        res = super(res_users, self).read(cr, uid, ids, fields, context, load)
        
        if 'commission' in fields:
            coms = self.browse(cr, uid, ids, context)
            for com in coms:
                year = com.years
                if not year:
                    today = date.today()
                    year = today.strftime("%Y")
            res[0].update(self._get_commission(cr, uid, ids, year, context))

        return res
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
            
        res = {}
        if 'groups_id' in vals and vals['groups_id'][0] and \
            vals['groups_id'][0] > 2:
            for group in self.pool.get('res.groups').browse(cr, uid, 
                                                    vals['groups_id'][0][2]):
                if group.name == 'Sale / Salesman':
                    vals['salesman'] = True
        
        res = super(res_users, self).create(cr, uid, vals, context)
        
        return res
    
    def write(self, cr, uid, ids, data, context=None):
        if 'years' in data:
            today = date.today()
            year = today.strftime("%Y")
            data['years'] = year
        
        if 'groups_id' in data and data['groups_id'][0] and \
            len(data['groups_id'][0]) > 2:
            for group in self.pool.get('res.groups').browse(cr, uid, 
                                                    data['groups_id'][0][2]):
                if group.name == 'Sale / Salesman':
                    data['salesman'] = True
                    
            if not 'salesman' in data:
                data['salesman'] = False
                   
        return super(res_users,self).write(cr, uid, ids, data, context)
    
    _columns = {
        'years':fields.selection(_get_year,'Years'),
        'commission': fields.one2many('res.commission', 'product', 'Commission'),
        'realised_total': fields.float('Réalise', readonly=True),
        'objective_total':fields.float('Objectif',readonly=True),
        'com1_total':fields.float('Com (1,5%)', readonly=True),
        'com2_total':fields.float('Com (2,5%)', readonly=True),
        'salesman': fields.boolean('Salesman'),
    }
    
    _defaults = {
        'salesman': lambda *a: False,
    }
    
res_users()


class cci_objectif(osv.osv):
    _name = 'cci.objectif'
    _columns = {
        'objective': fields.integer('Objectif'),
        'cci_product': fields.many2one('cci.product', 'Product'),
        'user' : fields.many2one('res.users', 'User'),
        'year': fields.char('Year', size=32),
    }
    
cci_objectif()


class res_commission(osv.osv):
    _name = 'res.commission'
    
    def _get_com1(self, cr, uid, ids, name, args, context=None):
        res = {}
        lines =  self.browse(cr, uid, ids, context=context)
        for line in lines:
            if not line.objectif or line.realised >= line.objectif:
                res[line.id] = 0
            else:
                res[line.id] = line.realised*0.015
        return res
    
    def _get_com2(self, cr, uid, ids, name, args, context=None):
        res = {}
        lines =  self.browse(cr, uid, ids, context=context)
        for line in lines:
            if not line.objectif or line.realised < line.objectif:
                res[line.id] = 0
            else:
                res[line.id] = line.realised*0.025
        return res
    
    _columns = {
        'product': fields.many2one('cci.product', 'Product', domain=[('commissioned', '=', True)], readonly=True),
        'realised': fields.integer('Realise', readonly=True),
        'objectif': fields.integer('Objectif'),
        'com1': fields.integer('Com (1.5%)'),
        'com2': fields.integer('Com (2.5%)'),
        'objective_id': fields.many2one('cci.objectif', 'Objective_id'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = {}
        if 'read' in context and context.get('read') == True:
            res = super(res_commission, self).create(cr, uid, vals, context)
        else:
            raise osv.except_osv('Action non permise!', 
                             'Vous ne pouvez pas ajouter de lignes')
        
        return res
    
    def write(self, cr, uid, ids, data, context=None):
        id =  self.browse(cr, uid, ids,context)[0]['objective_id']['id']
        self.pool.get('cci.objectif').write(cr, uid, id, {'objective':data['objectif']})
        return super(res_commission,self).write(cr,uid,ids,data,context)

res_commission()
