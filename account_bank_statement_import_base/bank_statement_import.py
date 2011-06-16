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


class account_bank_statement_import(osv.osv):
    
    _name = "account.bank.statement.import"
    _description = "account bank statement import"
    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'bank_statement_prefix': fields.char('Bank Statement Prefix', size=64, required=True),
        'journal_id':fields.many2one('account.journal', 'Journal'),
        'transferts_account_id':fields.many2one('account.account', 'Transferts Account'),
        'referential_id':fields.many2one('external.referential', 'Referential'),
        'credit_account_id':fields.many2one('account.account', 'Credit Account'),
        'fee_account_id':fields.many2one('account.account', 'Fee Account'),
        'scheduler': fields.many2one('ir.cron', 'scheduler', readonly=True),
        'rec_log': fields.text('log', readonly=True),

    }

    def action_import_bank_statement(self, cr, uid, ids, context=None):
        '''not implemented in this module'''
        return True

account_bank_statement_import()

class account_bank_statement(osv.osv):
    _inherit='account.bank.statement'
    
    def create(self, cr, uid, vals, context=None):
        if (not vals.get('period_id', False)) and vals.get('date', False):
            vals['period_id'] = self.pool.get('account.period').find(cr, uid, vals['date'], context=context)[0]
        return super(account_bank_statement, self).create(cr, uid, vals, context=context)
    
account_bank_statement()
