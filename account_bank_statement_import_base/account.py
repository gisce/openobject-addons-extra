# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    account_bank_statement_import_base for OpenERP                             #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc


class account_bank_statement(osv.osv):
    _inherit='account.bank.statement'
    
    _columns={
        'note': fields.text('Note'),
        'bank_statement_import_id': fields.many2one('account.bank.statement.import', 'Bank Statement Import'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if (not vals.get('period_id', False)) and vals.get('date', False):
            vals['period_id'] = self.pool.get('account.period').find(cr, uid, vals['date'], context=context)[0]
        return super(account_bank_statement, self).create(cr, uid, vals, context=context)
    
    def button_cancel(self, cr, uid, ids, context={}):
        print 'super cancel'
        done = []
        for st in self.browse(cr, uid, ids, context):
            if st.state=='draft':
                continue
            ids = []
            for line in st.line_ids:
                for move in line.move_ids:
                    for move_line in move.line_id:
                        if move_line.reconcile_id:
                            move_line.reconcile_id.unlink(context=context)
                ids += [x.id for x in line.move_ids]
            self.pool.get('account.move').unlink(cr, uid, ids, context)
            done.append(st.id)
        self.write(cr, uid, done, {'state':'draft'}, context=context)
        return True

    
    def button_auto_completion(self, cr, uid, ids, context=None):
        if not context:
            context={}
        stat_line_obj = self.pool.get('account.bank.statement.line')
        for stat in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            if stat.bank_statement_import_id:
                ctx['partner_id'] = stat.bank_statement_import_id.partner_id.id
                ctx['transferts_account_id'] = stat.bank_statement_import_id.transferts_account_id.id
                ctx['credit_account_id'] = stat.bank_statement_import_id.credit_account_id.id
                ctx['fee_account_id'] = stat.bank_statement_import_id.fee_account_id.id
                ctx['auto_completion'] = stat.bank_statement_import_id.auto_completion
                print stat.bank_statement_import_id.id
            for line in stat.line_ids:
                vals = stat_line_obj.auto_complete_line(cr, uid, line, context=ctx)
                if vals:
                    stat_line_obj.write(cr, uid, line.id, vals, context=ctx)
        return True
                        
                    
    
account_bank_statement()

class account_bank_statement_line(osv.osv):
    _inherit='account.bank.statement.line'
    
    
    _columns={
        'email_address': fields.char('Email', size=64),
        'order_ref': fields.char('Order Ref', size=64),
        'partner_name': fields.char('Partner Name', size=64),
        'label': fields.char('Label', size=64),
    }
    
    def auto_complete_line(self, cr, uid, line, context=None):
        res={}
        if not line.partner_id or line.account_id.id ==1:
            partner_obj = self.pool.get('res.partner')
            partner_id=False
            if line.order_ref:
                partner_id = partner_obj.get_partner_from_order_ref(cr, uid, line.order_ref, context=context)
            if not partner_id and line.email_address:
                partner_id = partner_obj.get_partner_from_email(cr, uid, line.email_address, context=context)
            if not partner_id and line.partner_name:
                partner_id = partner_obj.get_partner_from_name(cr, uid, line.partner_name, context=context)
            if partner_id:
                res = {'partner_id': partner_id}
            if context['auto_completion']:
                #Build the space for expr
                space = {
                            'self':self,
                            'cr':cr,
                            'uid':uid,
                            'line': line,
                            'context':context,
                        }
                exec context['auto_completion'] in space
                if space.get('result', False):
                    res.update(space['result'])
        return res
    
account_bank_statement_line()

class res_partner(osv.osv):
    _inherit='res.partner'
    
    def get_partner_from_order_ref(self, cr, uid, order_ref, context=None):
        order_obj = self.pool.get('sale.order')
        so_id = order_obj.search(cr, uid, [('name', '=', order_ref)], context=context)
        if so_id:
            so = order_obj.browse(cr, uid, so_id, context=context)[0]
            return so.partner_id.id
        return False
        
    def get_partner_from_name(self, cr, uid, partner_name, context=None):
        #print 'try to get partner from name', partner_name
        return False
        
    def get_partner_from_email(self, cr, uid, partner_email, context=None):
        address_ids = self.pool.get('res.partner.address').search(cr, uid, [['email', '=', partner_email]], context=context)
        if address_ids:
            partner_id = self.search(cr, uid, [['address', 'in', address_ids]], context=context)
            return partner_id and partner_id[0]
        return False

    def get_partner_from_label(self, cr, uid, line, context=None):
        supplier_ids = self.search(cr, uid, [['supplier', '=', True]], context=context)
        for partner in self.read(cr, uid, supplier_ids, ['name', 'property_account_payable', 'property_account_receivable'], context=context):
            if partner['name'] in line.label:
                return {'partner_id': partner['id'], 'account_id': line.amount>0 and partner['property_account_receivable'][0] or partner['property_account_payable'][0]}
        return {}


res_partner()
