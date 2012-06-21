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

import time
from report import report_sxw
import netsvc

class report_delivery_route_print(report_sxw.rml_parse):
    _name = 'report.delivery.route.print'
    _cr = None
    _uid = None
    def __init__(self, cr, uid, name, context):
        super(report_delivery_route_print, self).__init__(cr, uid, name, context)
        self._cr = cr
        self._uid = uid
        self.localcontext.update({
            'time': time,
            'convert': self.convert,
            'day': self.day,
            'month': self.month,
            'year': self.year,
        })

    def convert(self, amount, currency): return self.pool.get('ir.translation').amount_to_text(amount, 'pe', currency or 'Nuevo Sol')
    
    def day(self, date): return self.pool.get('ir.translation').date_part(date, 'day', format='number' ,lang='pe')
    
    def month(self, date): return self.pool.get('ir.translation').date_part(date, 'month', format='text' ,lang='pe')
    
    def year(self, date): return self.pool.get('ir.translation').date_part(date, 'year', format='number' ,lang='pe')
    
report_sxw.report_sxw(
    'report_delivery_route_print'
    'delivery.route',
    'addons/delivery_routes/report/delivery_route_print.rml',
    parser=report_delivery_route_print,header="external"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
