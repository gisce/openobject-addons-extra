# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006-2010 OpenERP S.A
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from report import report_sxw
from account.report.account_general_ledger import general_ledger

class general_ledger_report(general_ledger):
    _name = 'report.account.general.ledger_accounts'

    def set_context(self, objects, data, ids, report_type=None):
        obj_account = self.pool.get('account.account')
        self.account_ids = data['form'].get('account_ids', False)
        if (data['model'] == 'account.account'):
            new_ids = ids
            objects = obj_account.browse(self.cr, self.uid, new_ids)
            return super(general_ledger_report, self).set_context(objects, data, new_ids, report_type=report_type)
        data.update({'model': 'account.account'})
        if self.account_ids:
            new_ids = self.account_ids
        else:
            new_ids = [data['form']['chart_account_id']]
        objects = obj_account.browse(self.cr, self.uid, new_ids)
        return super(general_ledger_report, self).set_context(objects, data, new_ids, report_type=report_type)

report_sxw.report_sxw('report.account.general.ledger_accounts', 'account.account', 'addons/account/report/account_general_ledger.rml', parser=general_ledger_report, header='internal')
report_sxw.report_sxw('report.account.general.ledger_landscape_accounts', 'account.account', 'addons/account/report/account_general_ledger_landscape.rml', parser=general_ledger_report, header='internal landscape')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: