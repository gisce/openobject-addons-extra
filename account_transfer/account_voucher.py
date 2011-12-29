# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields
import netsvc
from tools.translate import _

class account_voucher(osv.osv):

    def _get_currency_id(self, cr, uid, ids, name, args, context=None):
        if context is None: context = {}
        res = {}
        journal_pool = self.pool.get('account.journal')
        user_pool = self.pool.get('res.users')
        for voucher in self.browse(cr, uid, ids, context=context):
            currency_id = user_pool.browse(cr, uid, uid,context=context).company_id.currency_id.id
            if voucher.journal_id:
                journal = journal_pool.browse(cr, uid, voucher.journal_id.id, context=context)
                if journal.currency:
                    currency_id = journal.currency.id
            res[voucher.id] = currency_id
        return res
    
    def _get_target_journals(self, cr, uid, ids, name, args, context={}):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            s = ""
            for line in voucher.line_ids:
                s += s and " / " or ""
                s += "%s: %s"%(line.account_journal_id.name,round(line.amount,2))
            res[voucher.id] = s
        return res
    
    _name = "account.voucher"
    _inherit = "account.voucher"
    _columns = {
            'balance_start': fields.related('account_id','balance', type='float', string='Current Balance', readonly=True, store=True),
            'currency_transfer_id': fields.function(_get_currency_id, type='many2one', relation='res.currency', string='Currency', readonly=True, method=True),
            'approve_user_id': fields.many2one('res.users', string='Approve User 1', readonly=True),
            'approve2_user_id': fields.many2one('res.users', string='Approve User 2', readonly=True),
            'transfer': fields.boolean('Is Transfer', select=True),
            'target_journals': fields.function(_get_target_journals, type="char", size=1024, method=True, string="Target Journals", readonly=True, store=True),
        }
    _defaults = {
            'transfer': False,
        }

    def onchange_journal_transfer(self, cr, uid, ids, journal_id, line_ids, tax_id, voucher_amount, partner_id=False, context=None):
        if not journal_id:
            return False
        voucher_line_pool = self.pool.get('account.voucher.line')
        #Se hicieron varias modificaciones en método onchange_journal de account_voucher
        vals = self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, context=context)
        vals['value']['currency_transfer_id'] = vals['value']['currency_id']
        prices = self.onchange_price_transfer(cr, uid, ids, line_ids, tax_id, voucher_amount, partner_id=partner_id, context=context)
        vals['value']['amount'] = prices['value']['amount']
        vals['value']['tax_amount'] = prices['value']['tax_amount']
        for line in line_ids:
            voucher_line_pool.unlink(cr,uid,line[1],context=context)
        vals['value']['line_ids'] = []
        return vals

    def onchange_price_transfer(self, cr, uid, ids, line_ids, tax_id, voucher_amount, partner_id=False, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        res = {
            'tax_amount': False,
            'amount': False,
        }
        voucher_total = 0.0
        voucher_line_ids = []

        total = 0.0
        total_tax = 0.0
        for line in line_ids:
            line_amount = 0.0
            line_amount = line[2] and line[2].get('currency_amount',0.0) or 0.0 
            voucher_line_ids += [line[1]]
            voucher_total += line_amount

        total = voucher_total

        if tax_id:
            tax = [tax_pool.browse(cr, uid, tax_id, context=context)]
            if partner_id:
                partner = partner_pool.browse(cr, uid, partner_id, context=context) or False
                taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
                tax = tax_pool.browse(cr, uid, taxes, context=context)

            if not tax[0].price_include:
                for tax_line in tax_pool.compute_all(cr, uid, tax, voucher_total, 1).get('taxes', []):
                    total_tax += tax_line.get('amount')
                total += total_tax
        
        res.update({'amount': total or voucher_total or voucher_amount,
                    'tax_amount': total_tax,
                    })
        return {
            'value':res
        }

    def action_confirm(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher in self.browse(cr,uid,ids,context=context):
            cur_ammount = 0.0
            for line in voucher.line_ids: cur_ammount += line.currency_amount
            if not cur_ammount:
                raise osv.except_osv('Error', _('Put the target journal and the target amount for this transfer'))
            elif round(voucher.amount,2) != round(cur_ammount,2):
                raise osv.except_osv('Error', _('The source amount is different to target  amount on this transfer'))
            wf_service.trg_create(uid, 'account.voucher', voucher.id, cr)
            self.write(cr, uid, [voucher.id], {'state':'proforma','currency_id':voucher.currency_transfer_id.id})
        return True

    def action_approve(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'account.voucher', voucher_id, cr)
        self.write(cr, uid, ids, {'approve_user_id':uid,'state':'proforma'})
        return True

    def action_approve_final(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher in self.browse(cr,uid,ids,context=context):
            if not voucher.approve_user_id:
                raise osv.except_osv('Error', _('Please, make the first approve'))
            if voucher.journal_id.jointly_transfer and voucher.approve_user_id.id == uid:
                raise osv.except_osv('Error', _('The same user cannot make the last approve'))
            wf_service.trg_create(uid, 'account.voucher', voucher.id, cr)
        self.write(cr, uid, ids, {'approve2_user_id':uid})
        self.proforma_voucher(cr,uid,ids,context=context)
        return True

    def cancel_voucher(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'approve2_user_id':None,'approve_user_id':None})
        return super(account_voucher,self).cancel_voucher(cr, uid, ids, context=context)

account_voucher()

class account_voucher_line(osv.osv):
    
    def _get_currency_id(self, cr, uid, ids, name, args, context=None):
        if context is None: context = {}
        res = {}
        journal_pool = self.pool.get('account.journal')
        user_pool = self.pool.get('res.users')
        for line in self.browse(cr, uid, ids, context=context):
            currency_id = user_pool.browse(cr, uid, uid,context=context).company_id.currency_id.id
            if line.account_journal_id:
                journal = journal_pool.browse(cr, uid, line.account_journal_id.id, context=context)
                if journal.currency:
                    currency_id = journal.currency.id
            res[line.id] = currency_id
        return res
    
    _name = "account.voucher.line"
    _inherit = "account.voucher.line"
    _columns = {
            'balance_start': fields.related('account_id','balance', type='float', string='Current Balance', readonly=True, store=True),
            'account_journal_id': fields.many2one('account.journal', string='Destination Journal'),
            'currency_id': fields.function(_get_currency_id, type='many2one', relation='res.currency', string='Currency', store=True, readonly=True, method=True),
            'currency_amount': fields.float('Currency Amount'),
            'exchange_rate': fields.float('Exchange Rate', digits=(16,6)),
        }
    _defaults = {
            'exchange_rate' : 1.0,
        }

    def onchange_journal_transfer(self, cr, uid, ids, journal_id, source_journal_id,voucher_amount, line_ids, tax_id=False, partner_id=False, context=None):
        if not journal_id:
            return False
            
        vals = {'value':{}}
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        journal_source = journal_pool.browse(cr, uid, source_journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        balance = 0.0
        if account_id :
            balance = account_id.balance

        #vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
        currency_id = journal.company_id.currency_id.id
        currency = journal.company_id.currency_id
        currency_source = journal_source.company_id.currency_id
        if journal.currency:
            currency_id = journal.currency.id
            currency = journal.currency
        if journal_source.currency:
            currency_source = journal_source.currency
            
        if journal.company_id.currency_id.id != currency_id:
            balance = balance * journal.currency.rate / journal.company_id.currency_id.rate
        amount = 0.0
        if len(line_ids) < 2: amount = voucher_amount
        
        exchange_rate = currency.rate and (currency_source.rate / currency.rate) or 1.0
        
        vals['value'].update({'balance_start':balance})
        vals['value'].update({'currency_amount':(amount)})
        vals['value'].update({'currency_id':currency_id})
        vals['value'].update({'account_id':account_id.id})
        vals['value'].update({'amount':amount/exchange_rate})
        vals['value'].update({'exchange_rate':exchange_rate})
        vals['value'].update({'type':'dr'})
        
        if journal_id == source_journal_id:
            vals['warning'] = {'title':'Warning','message':_('You cannot use the same cash/bank journal as source and target')}
        return vals

    def onchange_line_price_transfer(self, cr, uid, ids, amount, exchange_rate, context=None):
        return {
            'value':{'currency_amount': amount * exchange_rate,}
        }
                
account_voucher_line()
