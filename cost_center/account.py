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


class account_account_type(osv.osv):
    _name = 'account.account.type'
    _inherit = 'account.account.type'
    _columns = {
            'is_cost_center': fields.boolean('Cost Center'),
        }
    _defaults = {
            'is_cost_center': False,
        }

account_account_type()


class account_account(osv.osv):
    _name = 'account.account'
    _inherit = 'account.account'
    _columns = {
            'is_cost_center': fields.related('user_type','is_cost_center',type='boolean',string="Cost Center",readonly=True),
        }

account_account()


class account_journal(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'
    _columns = {
        'charge_account_id' : fields.many2one('account.account',
                                               string="Charge Account",
                                               domain=[('type','<>','view'), ('type', '<>', 'closed')],
                                               help="Credit account to make a aditional journal entry, like to charge account in a cost center"),
        }

account_journal()

class account_move_line(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'
    _columns = {
            'related_account_id' : fields.many2one('account.account',
                                                string="Related Account",
                                                domain=[('type','<>','view'), ('type', '<>', 'closed')], 
                                                help="This account must be used to register the related cost center account or the expense account (destinity of cost center)"),
        }

account_move_line()