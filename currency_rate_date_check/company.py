# -*- encoding: utf-8 -*-
##############################################################################
#
#    Currency rate date check module for OpenERP
#    Copyright (C) 2012 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'currency_rate_max_delta': fields.integer('Max time delta in days for currency rates', help="This is the maximum interval in days between the date associated with the amount to convert and the currency rate available in OpenERP with the nearest date."),
    }

    _defaults = {
        'currency_rate_max_delta': lambda *a: 7,
    }

    def _check_currency_rate_max_delta(self, cr, uid, ids):
        for company in self.read(cr, uid, ids, ['currency_rate_max_delta']):
            if company['currency_rate_max_delta'] >= 0:
                continue
            else:
                return False
        return True

    _constraints = [
        (_check_currency_rate_max_delta, "The value must be positive", ['currency_rate_max_delta']),
    ]

res_company()
