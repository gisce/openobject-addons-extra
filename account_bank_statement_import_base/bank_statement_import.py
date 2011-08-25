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
from datetime import datetime
from tools.translate import _

class account_bank_statement_import(osv.osv):
    
    _name = "account.bank.statement.import"
    _description = "account bank statement import"
    

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'bank_statement_prefix': fields.char('Bank Statement Prefix', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Bank Partner'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'transferts_account_id':fields.many2one('account.account', 'Transferts Account'),
        'shop_id':fields.many2one('sale.shop', 'Sale Shop'),
        'credit_account_id':fields.many2one('account.account', 'Credit Account'),
        'fee_account_id':fields.many2one('account.account', 'Fee Account'),
        'scheduler': fields.many2one('ir.cron', 'scheduler', readonly=True),
        'rec_log': fields.text('log', readonly=True),
        'bank_statement_ids': fields.one2many('account.bank.statement', 'bank_statement_import_id', 'Bank Statement Imported'),
        'last_import_date': fields.date("Last Import Date"),
        'merge_fee': fields.boolean("Merge Fee"),
        'auto_completion': fields.text('Auto Completion'),
    }

    def launch_import_bank_statement(self, cr, uid, ids, context=None):
        stat_obj = self.pool.get('account.bank.statement')
        for id in ids:
            logger = netsvc.Logger()
            res = self.action_import_bank_statement(cr, uid, id, context)
            #autocomplete bank statement
            stat_obj.button_auto_completion(cr, uid, res['crids'], context=context)
            stat_obj.auto_confirm(cr, uid, res['crids'], context=context)
            log = self.read(cr, uid, id, ['rec_log'], context=context)['rec_log']
            log_line = log and log.split("\n") or []
            log_line[0:0] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' : ' + str(len(res['crids'])) + _(' bank statement have been imported and ' + str(len(res['exist_ids'])) + _(' bank statement already exist'))]
            log = "\n".join(log_line)
            self.write(cr, uid, id, {'rec_log' : log}, context=context)
            logger.notifyChannel('banck statement import', netsvc.LOG_INFO, "%s bank statement have been imported and %s bank statement already exist"%(len(res['crids']), len(res['exist_ids'])))
        return True

    def action_import_bank_statement(self, cr, uid, id, context=None):
        '''not implemented in this module'''
        return {}
    
    def open_bank_statement(self, cr, uid, ids, context):
        task = self.browse(cr, uid, ids, context=context)[0]
        
        return {
            'name': 'Bank ',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [252],
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': self.read(cr, uid, ids, ['bank_statement_ids'],context=context)[0]['bank_statement_ids'],
        }

account_bank_statement_import()
