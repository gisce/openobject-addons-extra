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

    #This code should be excuted in an other module
class account_move(osv.osv):
    _inherit='account.move'
    def unlink(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            for move_line in move.line_id:
                if move_line.reconcile_id:
                    move_line.reconcile_id.unlink(context=context)
        return super(account_move, self).unlink(cr, uid, ids, context=context)
account_move()



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

    #This code should be excuted in an other module
    def button_cancel(self, cr, uid, ids, context={}):
        done = []
        for st in self.browse(cr, uid, ids, context=context):
            if st.state=='draft':
                continue
            ids = []
            for line in st.line_ids:
                for move in line.move_ids:
                    move.button_cancel(context=context)
                    move.unlink(context=context)
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
            for line in stat.line_ids:
                vals = stat_line_obj.auto_complete_line(cr, uid, line, context=ctx)
                if not line.ref and not vals.get('ref', False):
                    vals['ref'] = stat.name
                if vals:
                    stat_line_obj.write(cr, uid, line.id, vals, context=ctx)
        return True
                        
    def auto_confirm(self, cr, uid, ids, context=None):
        if not context:
            context={}
        ok=True
        for stat in self.browse(cr, uid, ids, context=context):
            for line in stat.line_ids:
                if not line.partner_id or line.account_id.id == 1:
                    ok=False
                    continue
            if ok:
                self.button_confirm(cr, uid, [stat.id], context=context)
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
    
    #this should be done in an external module
    def onchange_partner_id(self, cr, uid, line_id, partner_id, line_type, currency_id, context={}):
        if line_id:
            if type(line_id) == list:
                id = line_id[0]
            else:
                id=line_id
            line = self.browse(cr, uid, id, context=context)
            if line.statement_id.state == 'confirm':
                cr.execute('Update account_move_line set partner_id = %s where id in %s' %(partner_id, tuple([line.id for line in line.move_ids[0].line_id])))
                cr.execute('Update account_bank_statement_line set partner_id = %s where id = %s' %(partner_id, line_id[0]))
        return super(account_bank_statement_line, self).onchange_partner_id(cr, uid, line_id, partner_id, line_type, currency_id, context={})
    
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
            if not partner_id and line.label:
                partner_id = partner_obj.get_partner_from_label_based_on_bank_statement_label(cr, uid, line.label, context=context)
            if partner_id:
                res = {'partner_id': partner_id}
            if context['auto_completion']:
                #Build the space for expr
                space = {
                            'self':self,
                            'cr':cr,
                            'uid':uid,
                            'line': line,
                            'res': res,
                            'context':context,
                        }
                exec context['auto_completion'] in space
                if space.get('result', False):
                    res.update(space['result'])
        return res
    
account_bank_statement_line()
