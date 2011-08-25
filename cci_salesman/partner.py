# -*- coding: utf-8 -*-

from osv import osv
from osv import fields
from datetime import date

import time


class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'

    _columns = {
        'name': fields.related('address_id', 'partner_id', type='many2one',
                               relation='res.partner', string='Partenaire',
                               store=True),
    }
res_partner_job()


class cci_product(osv.osv):
    _name = 'cci.product'

    _columns = {
        'name': fields.char('Produit', size=64, required=True),
        'categories': fields.one2many('cci.product.category', 'cci_product',
                                      'Categories'),
        'commissioned': fields.boolean('Commissioné'),
        'order_type': fields.selection([('participation', 'Participation'),
                                        ('order', 'Devis'),
                                        ('membership', 'Adhésion')],
                                       'Type de BDC')
    }
cci_product()


class cci_product_category(osv.osv):
    _name = 'cci.product.category'

    _columns = {
        'name': fields.char('Catégorie', size=64, required=True),
        'cci_product': fields.many2one('cci.product', 'Produit', 
                                       required=True),
        'product': fields.many2one('product.product', 'Intitulé comptable', 
                                   required=True),
    }
cci_product_category()


class crm_case(osv.osv):
    _inherit = 'crm.case'
    
    _columns = {
        'product': fields.many2one('cci.product', 'Produit'),
        'product_category' : fields.many2one('cci.product.category',
                                              'Catégorie'),
    }    
crm_case()


class cci_contact(osv.osv):
    _name = 'cci.contact'

    _columns = {
        'name': fields.char('Nom', size=64, required=True),
        'user': fields.many2one('res.users', 'Utilisateur', required=True),
    }
cci_contact()


class res_partner_interest(osv.osv):
    _name = 'res.partner.interest'
    
    def _get_orders(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for interest in self.browse(cr, uid, ids, context=context):
            if interest.category:
                product_id = interest.category.product.id
                partner_id = interest.partner.id
                year = interest.partner.year
                
                cr.execute("SELECT sum(ail.price_subtotal) \
                            FROM account_invoice_line ail, account_invoice ai \
                            WHERE ail.invoice_id = ai.id \
                            AND ai.partner_id = " + str(partner_id) + 
                            " AND ail.product_id = " + str(product_id) + 
                            " AND ai.state in ('open', 'paid')")
                value = cr.fetchone()
                if value[0]:
                    res[interest.id] = value[0]
                else:
                    res[interest.id] = False
            else:
                res[interest.id] = False 
        
        return res
    
    _columns = {
        'partner': fields.many2one('res.partner', 'Partenaire'),
        'date': fields.date('Date'),
        'product': fields.many2one('cci.product', 'Produit'),
        'cci_contact': fields.many2one('cci.contact', 'Contact CCI'),
        'contact': fields.many2one('res.partner.job', 'Contact client'),
        'category': fields.many2one('cci.product.category', 'Catégorie'),
        'turnover_hoped': fields.integer('CA espéré'),
        'orders': fields.function(_get_orders, method=True, type='float', 
                                  digits=(16, 2), string='BDC'), 
        'next_action': fields.date('Prochaine action'),
        'cci_contact_follow': fields.many2one('res.users', 
                                              'Contact CCI Suivi'),
        'description': fields.char('Description/commentaire', size=1024),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        
        crm_section_obj = self.pool.get('crm.case.section')
        partner = False
        description = ''
        next_action = False
            
        if 'partner' in vals:
            partner = vals['partner']
        
        if 'description' in vals and vals['description']:
            description = vals['description']
            
        if 'next_action' in vals:
                next_action = vals['next_action']

        section_id = crm_section_obj.search(cr, uid, 
                                            [('code', '=', 'CRMInt')])[0]
        
        if 'cci_contact_follow' in vals and section_id:
            id = self.pool.get('crm.case').create(cr, uid, 
                                    {'partner_id': partner,
                                     'date': time.strftime('%Y-%m-%d'),
                                     'user_id': vals['cci_contact_follow'],
                                     'name': description,
                                     'section_id': section_id,
                                     'date_deadline': next_action,
                                     'product': vals['product'],
                                     'product_category': vals['category'],
                                     'planned_revenue':vals['turnover_hoped'],
                                     }, context),
                                     
        res_id = super(res_partner_interest, self).create(cr, uid, 
                                                          vals, context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
            
        crm_section_obj = self.pool.get('crm.case.section')
            
        interest = self.browse(cr, uid, ids, context)[0]
        
        partner = interest.partner.id
        
        if 'description' in vals and vals['description']:
            description = vals['description']
        elif interest.description:
            description = interest.description
        else:
            description = ''
            
        if 'next_action' in vals:
            next_action = vals['next_action']
        else:
            next_action = interest.next_action
            
        section_id = crm_section_obj.search(cr, uid, 
                                            [('code', '=', 'CRMInt')])[0]

        cci_contact_follow = self.browse(cr, uid, ids[0]).cci_contact_follow.id
        
        if 'cci_contact_follow' in vals and \
            cci_contact_follow <> vals['cci_contact_follow'] and section_id:
            self.pool.get('crm.case').create(cr, uid, 
                                    {'partner_id': partner,
                                     'date': time.strftime('%Y-%m-%d'),
                                     'user_id': vals['cci_contact_follow'],
                                     'name': description,
                                     'section_id': section_id,
                                     'date_deadline': next_action,
                                     'product': vals['product'],
                                     'product_category': vals['category'],
                                     'planned_revenue':vals['turnover_hoped'],
                                     }, context)
        res = super(res_partner_interest, self).write(cr, uid, 
                                                      ids, vals, context)
        return res
    
res_partner_interest()


class res_partner_interest_next(osv.osv):
    _name = 'res.partner.interest.next'
    
    def _get_orders(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for interest in self.browse(cr, uid, ids, context=context):
            if interest.category:
                product_id = interest.category.product.id
                partner_id = interest.partner.id
                year = str(interest.partner.year)
                
                cr.execute("SELECT sum(ail.price_subtotal) \
                            FROM account_invoice_line ail, account_invoice ai \
                            WHERE ail.invoice_id = ai.id \
                            AND ai.partner_id = " + str(partner_id) + 
                            " AND ail.product_id = " + str(product_id) +
                            " AND ai.date_invoice BETWEEN '" + year + 
                            "-01-01' AND '" + year + "-12-31' " + 
                            "AND ai.state in ('open', 'paid')")
                value = cr.fetchone()
                if value[0]:
                    res[interest.id] = value[0]
                else:
                    res[interest.id] = False
            else:
                res[interest.id] = False 
        
        return res
    
    _columns = {
        'partner': fields.many2one('res.partner', 'Partenaire'),
        'date': fields.date('Date'),
        'product': fields.many2one('cci.product', 'Produit'),
        'cci_contact': fields.many2one('cci.contact', 'Contact CCI'),
        'contact': fields.many2one('res.partner.job', 'Contact client'),
        'category': fields.many2one('cci.product.category', 'Catégorie'),
        'turnover_hoped': fields.integer('CA espéré'),
        'orders': fields.function(_get_orders, method=True, type='float', 
                                  digits=(16, 2), string='BDC'), 
        'next_action': fields.date('Prochaine action'),
        'cci_contact_follow': fields.many2one('res.users', 
                                              'Contact CCI Suivi'),
        'description': fields.char('Description/commentaire', size=1024),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        
        crm_section_obj = self.pool.get('crm.case.section')
        partner = False
        description = ''
        next_action = False

        if not context.get('next'):
            if 'partner' in vals:
                partner = vals['partner']
            
            if 'description' in vals and vals['description']:
                description = vals['description']
                
            if 'next_action' in vals:
                next_action = vals['next_action']
    
            section_id = crm_section_obj.search(cr, uid, 
                                                [('code', '=', 'CRMInt')])[0]
            
            if 'cci_contact_follow' in vals and section_id:
                id = self.pool.get('crm.case').create(cr, uid, 
                                        {'partner_id': partner,
                                         'date': time.strftime('%Y-%m-%d'),
                                         'user_id': vals['cci_contact_follow'],
                                         'name': description,
                                         'section_id': section_id,
                                         'date_deadline': next_action,
                                         'product': vals['product'],
                                         'product_category': vals['category'],
                                         'planned_revenue':vals['turnover_hoped'],
                                         }, context)
        res_id = super(res_partner_interest_next, self).create(cr, uid, 
                                                          vals, context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        crm_section_obj = self.pool.get('crm.case.section')
            
        interest = self.browse(cr, uid, ids, context)[0]
        
        partner = interest.partner.id
        
        if 'description' in vals and vals['description']:
            description = vals['description']
        elif interest.description:
            description = interest.description
        else:
            description = ''
            
        if 'next_action' in vals:
            next_action = vals['next_action']
        else:
            next_action = interest.next_action
        
        section_id = crm_section_obj.search(cr, uid, 
                                            [('code', '=', 'CRMInt')])[0]

        cci_contact_follow = self.browse(cr, uid, ids[0]).cci_contact_follow.id
        
        if cci_contact_follow <> vals['cci_contact_follow'] and section_id:
            self.pool.get('crm.case').create(cr, uid, 
                                    {'partner_id': partner,
                                     'date': time.strftime('%Y-%m-%d'),
                                     'user_id': vals['cci_contact_follow'],
                                     'name': description,
                                     'section_id': section_id,
                                     'date_deadline': next_action,
                                     'product': vals['product'],
                                     'product_category': vals['category'],
                                     'planned_revenue':vals['turnover_hoped'],
                                     }, context)
        res = super(res_partner_interest_next, self).write(cr, uid, 
                                                      ids, vals, context)
        return res
    
res_partner_interest_next()


class res_partner_history(osv.osv):
    _name = 'res.partner.history'
    _rec_name = 'description'

    _columns = {
        'partner': fields.many2one('res.partner', 'Partenaire'),
        'date': fields.date('Date'),
        'cci_contact': fields.many2one('cci.contact', 'Contact CCI'),
        'contact': fields.many2one('res.partner.job', 'Contact client'),
        'action': fields.selection([
            ('appel_sortant','Appel sortant'),
            ('commando','Commando'),
            ('mail','Mail'),
            ('meeting_cci','Meeting CCI'),
            ('meeting_externe','Meeting externe'),
            ('midi','Midi'),
            ('rdv','RDV'),], 'Action'),
        'product': fields.many2one('cci.product', 'Produit'),
        'category': fields.many2one('cci.product.category', 'Catégorie'),
        'description': fields.char('Description/commentaire', size=1024),
    }

res_partner_history()


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _get_year(self,cr,uid,context):
        today = date.today()
        currentYear = today.strftime("%Y")
        
        yearTab = []
        for i in xrange(int(currentYear), 2007, -1):
            yearTab.append((str(i),str(i)))

        return tuple(yearTab)

    def _get_turnover(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for partner in self.browse(cr, uid, ids, context):
            turnover = 0
            for interest in partner.interest_year:
                turnover += interest.turnover_hoped
            
            res[partner.id] = turnover
        return res
        
    def _get_turnover_next(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for partner in self.browse(cr, uid, ids, context):
            turnover = 0
            for interest in partner.interest_next_year:
                turnover += interest.turnover_hoped
            
            res[partner.id] = turnover
        return res
        
        return res
    
    def _get_orders(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for partner in self.browse(cr, uid, ids, context):
            
            if partner.year == False:
                year = str(time.strftime('%Y'))
            else:
                year = str(partner.year)
            
            cr.execute("SELECT sum(ail.price_subtotal) \
                        FROM account_invoice_line ail, account_invoice ai \
                        WHERE ail.invoice_id = ai.id \
                        AND ai.partner_id = " + str(partner.id) + 
                        " AND ai.date_invoice BETWEEN '" + year + 
                        "-01-01' AND '" + year + "-12-31' " + 
                        "AND ai.state in ('open', 'paid')")
            value = cr.fetchone()
            
            if value[0]:
                res[partner.id] = value[0]
            else:
                res[partner.id] = False
        
        return res
        
    def _get_orders_next(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for partner in self.browse(cr, uid, ids, context):
            
            if partner.year == False:
                year = str(time.strftime('%Y'))
            else:
                year =str(partner.year + 1)
            
            cr.execute("SELECT sum(ail.price_subtotal) \
                        FROM account_invoice_line ail, account_invoice ai \
                        WHERE ail.invoice_id = ai.id \
                        AND ai.partner_id = " + str(partner.id) + 
                        " AND ai.date_invoice BETWEEN '" + year + 
                        "-01-01' AND '" + year + "-12-31' " + 
                        "AND ai.state in ('open', 'paid')")
            value = cr.fetchone()
            
            if value[0]:
                res[partner.id] = value[0]
            else:
                res[partner.id] = False
        
        return res

    _columns = {
        'year': fields.integer('Year'),
        'tunover_hoped': fields.function(_get_turnover, method=True, 
                                 type='float', 
                                 digits=(16, 2), string='Total CA espéré'),
        'tunover_hoped_next': fields.function(_get_turnover_next, method=True, 
                                 type='float', 
                                 digits=(16, 2), string='Total CA espéré'),
        'orders': fields.function(_get_orders, method=True, 
                         type='float', 
                         digits=(16, 2), string='Total BDC saison en cours'),
        'orders_next': fields.function(_get_orders_next, method=True, 
                         type='float', 
                         digits=(16, 2), string='Total BDC saison prochaine'),
        'history': fields.one2many('res.partner.history', 'partner',
                                  'Historique'),
        'interest_year': fields.one2many('res.partner.interest', 'partner', 
                                    'Marque d\'intéret (saison en cours)'),
        'cci_turnovers': fields.one2many('cci.turnover', 'partner', 
                                         'Turnovers'),
        'interest_next_year': fields.one2many('res.partner.interest.next', 
                                              'partner', 
                                    'Marque d\'intéret (saison prochaine)'),
        'years': fields.selection(_get_year,'Years'),
        'total': fields.integer('Total'),
    }
    
    _defaults = {
        'year': lambda *a: int(time.strftime('%Y')),
    }
    
    def year_changed(self, cr, uid, ids, years):
        res = self.read(cr, uid, ids, ['cci_turnovers', 'years'], 
                        context={'years': int(years)})
        return {'value': res[0]}
                                                                     
    def read(self, cr, uid, ids, fields, context=None, load='_classic_read'):
        res = {}
        res = super(res_partner, self).read(cr, uid, ids, fields, context, load)
        cci_product_obj = self.pool.get('cci.product')

        if 'cci_turnovers' in fields:
            turnover_obj = self.pool.get('cci.turnover')
            
            # remove all turnovers
            all_turnovers = turnover_obj.search(cr, uid, [])
            turnover_obj.unlink(cr, uid, all_turnovers)
            
            cr.execute("""
                SELECT cp.id AS product_name,
                    ai.partner_id,
                    date_part('year', ai.date_invoice) AS date_year,
                    SUM(ail.price_subtotal) AS total
                FROM account_invoice ai
                    INNER JOIN account_invoice_line ail
                        ON ai.id = ail.invoice_id
                    INNER JOIN product_product p
                        ON ail.product_id = p.id
                    INNER JOIN cci_product_category cpc
                        ON ail.product_id = cpc.product
                    INNER JOIN cci_product cp
                        ON cp.id = cpc.cci_product 
                WHERE ai.state in ('open', 'paid') 
                GROUP BY cp.id, ai.partner_id, date_year
            """)
            lines = cr.fetchall()
            
            # relink new turnover
            res[0]['cci_turnovers'] = []
            
            total = 0
            for line in lines:
                # computes new turnovers
                if 'years' in res[0] and not res[0]['years']:
                    res[0]['years'] = int(time.strftime('%Y'))
                
                if context and context.has_key('years'):
                    res[0]['years'] = context['years']

                if 'years' in res[0] and ids[0] == line[1] and \
                    int(res[0]['years']) == int(line[2]):
                    data = {
                        'cci_product': line[0],
                        'partner': line[1],
                        'sum_price': line[3],
                        'years': res[0]['years']
                    }
                    turnover_id = turnover_obj.create(cr, uid, data, context)
                    res[0]['cci_turnovers'].append(turnover_id)
                    total += line[3]
                    
            cci_product_ids = cci_product_obj.search(cr, uid, [])
            
            if context and context.has_key('years'):
                years = context['years']
            else:
                years = int(time.strftime('%Y'))
            
            for partner_id in ids:
                for cci_product_id in cci_product_ids:
                    turnover_ids = turnover_obj.search(cr, uid, 
                                        [('partner', '=', partner_id), 
                                        ('cci_product', '=', cci_product_id)])
                    
                    if not turnover_ids:
                        data = {
                            'cci_product': cci_product_id,
                            'partner': partner_id,
                            'sum_price': 0,
                            'years': years,
                        }
                        turnover_id = turnover_obj.create(cr, uid, data, 
                                                          context)
                        res[0]['cci_turnovers'].append(turnover_id)
                
            res[0]['total'] = total
                            
        return res

res_partner()


class cci_turnover(osv.osv):
    _name = 'cci.turnover'
    _rec_name = 'cci_product'
    
    def read(self, cr, uid, ids, fields, context=None, load='_classic_read'):
        res = super(cci_turnover, self).read(cr, uid, ids, fields, context, load)
        if 'details' in fields:
            detail = self.browse(cr, uid, ids[0], context)
            detail_obj = self.pool.get('cci.turnover.details')
            
            # remove all details
            all_details = detail_obj.search(cr, uid, [])
            detail_obj.unlink(cr, uid, all_details)
            
            cr.execute("""
            SELECT ai.number, cp.name || ' ' || cpc.name AS product, ail.price_subtotal
            FROM account_invoice ai
                INNER JOIN account_invoice_line ail
                    ON ai.id = ail.invoice_id
                INNER JOIN product_product p
                    ON ail.product_id = p.id
                INNER JOIN cci_product_category cpc
                    ON ail.product_id = cpc.product
                INNER JOIN cci_product cp
                    ON cp.id = cpc.cci_product
           WHERE cp.id = %s
                AND ai.partner_id = %s
                AND date_part('year', ai.date_invoice) = %d 
                AND ai.state in ('open', 'paid') 
            """ % (detail.cci_product.id, 
                   detail.partner.id,
                   int(detail.years)))
            lines = cr.fetchall()
            
            total = 0
            for line in lines:
                data = {
                        'invoice_number': line[0],
                        'product_name': line[1],
                        'price': line[2],
                    }
                detail_id = detail_obj.create(cr, uid, data, context)
                res[0]['details'].append(detail_id)
                total += line[2]
            res[0]['total'] = total
        
        return res
    
    _columns = {
        'cci_product': fields.many2one('cci.product', 'Product'),
        'sum_price': fields.integer('Montant'),
        'partner': fields.many2one('res.partner', 'Partner'),
        'details': fields.one2many('cci.turnover.details', 'turnover', 'Details'),
        'years': fields.char('years', size=4),
        'total': fields.integer('Total'),
    }

cci_turnover()


class cci_turnover_details(osv.osv):
    _name = 'cci.turnover.details'
    _rec_name = 'product_name'
    
    _columns = {
        'invoice_number': fields.char('FactureNo', size=64),
        'product_name': fields.char('Produit', size=64),
        'price': fields.integer('Montant'),
        'turnover': fields.many2one('cci.turnover', 'Turnover'),
    }

cci_turnover_details()
