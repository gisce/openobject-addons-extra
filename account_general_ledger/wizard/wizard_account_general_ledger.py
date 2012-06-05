# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv

class account_general_ledger(osv.osv_memory):
    _inherit = "account.report.general.ledger"
    _description = "Account General Ledger"
    _columns = {
        'account_ids': fields.many2many('account.account', 'account_general_ledger_rel', 'general_ledger_id', 'account_id', 'Accounts'),
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        res = super(account_general_ledger, self)._print_report(cr, uid, ids, data, context=context)
        res['datas']['form'].update(self.read(cr, uid, ids, ['account_ids'])[0])
        if res['datas']['form']['landscape']:
            return { 'type': 'ir.actions.report.xml', 'report_name': 'account.general.ledger_landscape_accounts', 'datas': res['datas']}
        return { 'type': 'ir.actions.report.xml', 'report_name': 'account.general.ledger_accounts', 'datas': res['datas']}

account_general_ledger()   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    