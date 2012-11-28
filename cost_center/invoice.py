# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
import time
import netsvc

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
            'account_cc_id' : fields.many2one('account.account', 'Cost Center', domain=[('type','<>','view'), ('type', '<>', 'closed'), ('is_cost_center','=',True)], help="Debit account to make a aditional journal entry like to cost center account"),
            'account_ch_id' : fields.related('invoice_id','journal_id','charge_account_id', type='many2one', string='Account Charge', help="Credit account to make a aditional journal entry like to charge account"),
        }

    def onchange_analytic_id(self, cr, uid, ids, account_analytic_id):
        res = {'value':{}}
        if not account_analytic_id:
            return res
        account_obj = self.pool.get('account.analytic.account').browse(cr, uid, account_analytic_id)
        res['value']['account_cc_id'] = account_obj.account_cost_center and account_obj.account_cost_center.id or False
        return res

account_invoice_line()

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    def _refund_cleanup_lines(self, cr, uid, lines):
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        i = 0
        for r in res:
            for field in ('account_cc_id',):
                r[2][field] = lines[i].get(field, False) and lines[i][field][0]
            i+=1
        return res
    
    
    def finalize_invoice_move_lines(self, cr, uid, inv, lines):
        res = super(account_invoice, self).finalize_invoice_move_lines(cr, uid, inv, lines)
        currency_id = False
        company_currency = inv.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        date = inv.date_invoice or time.strftime('%Y-%m-%d')
        if company_currency != inv.currency_id.id:
            currency_id = inv.currency_id.id
        account_ch_id = inv.journal_id.charge_account_id
        for l in inv.invoice_line:
            if l.account_cc_id and account_ch_id:
                amount_currency = 0.0
                debit = 0.0
                credit = 0.0
                amount = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, l.price_subtotal, context={'date': inv.date_invoice})
                if currency_id:
                    amount_currency = l.price_subtotal
                if inv.type in ('in_invoice', 'out_refund'):
                    debit = amount
                else:
                    credit = amount
                cc = [(0,0,{
                        'analytic_account_id': False, 
                        'tax_code_id': False, 
                        'analytic_lines': [], 
                        'tax_amount': 0.0, 
                        'name': l.name, 
                        'ref': False, 
                        'currency_id': currency_id, 
                        'debit': debit,
                        'credit': credit, 
                        'product_id': l.product_id.id, 
                        'date_maturity': False, 
                        'date': date,
                        'amount_currency': amount_currency, 
                        'product_uom_id': l.uos_id.id, 
                        'quantity': l.quantity, 
                        'partner_id': l.partner_id.id, 
                        'account_id': l.account_cc_id.id,
                        'related_account_id': l.account_id.id
                        }),
                    (0,0,{
                        'analytic_account_id': False, 
                        'tax_code_id': False, 
                        'analytic_lines': [], 
                        'tax_amount': 0.0, 
                        'name': l.name, 
                        'ref': False, 
                        'currency_id': currency_id, 
                        'debit': credit,
                        'credit': debit, 
                        'product_id': l.product_id.id, 
                        'date_maturity': False, 
                        'date': date,
                        'amount_currency': amount_currency, 
                        'product_uom_id': l.uos_id.id, 
                        'quantity': l.quantity, 
                        'partner_id': l.partner_id.id, 
                        'account_id': account_ch_id.id,
                    })]
                res = res + cc

        return res

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
