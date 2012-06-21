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
from tools.translate import _
import time


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def _get_route_line_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req= """
                        SELECT c.id AS func_id
                        FROM delivery_route_line c
                        WHERE
                          (c.picking_id = %d)
                        """ % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res
        
    def _get_route_id(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req= """
                        SELECT r.id AS func_id
                        FROM delivery_route_line c, delivery_route r
                        WHERE c.route_id = r.id and 
                          (c.picking_id = %d)
                        """ % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res
                
    def _get_route_state(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for i in ids:
            sql_req= """
                        SELECT c.state AS func_id
                        FROM delivery_route_line c
                        WHERE
                          (c.picking_id = %d)""" % (i,)
            cr.execute(sql_req)
            sql_res = cr.dictfetchone()

            if sql_res:
                res[i] = sql_res['func_id']
            else:
                res[i] = False
        return res

    _columns = {
            'delivery_date': fields.date('Delivery Date'),
            'time_id': fields.many2one('delivery.time','Delivery Time',help='Delivery time or turn to receive'),
            'route_line_id': fields.function(_get_route_line_id,type='many2one',obj='delivery.route.line',
                            method=True,string='Delivery Route Line',readonly=True,store=False),
            'route_id': fields.function(_get_route_id,type='many2one',obj='delivery.route',
                            method=True,string='Delivery Route',readonly=True,store=False),
            'route_state' : fields.function(_get_route_state,type="char",method=True,string="Route State",readonly=True,
                            store=False),
            'delivered': fields.boolean('Is Delivered',select=True),
        }
    _defaults = {
            'delivered': False,
        }

    def write(self, cr, uid, ids, vals, context=None):
        if 'delivered' in vals.keys():
            for o in self.browse(cr, uid, ids, context=context):
                if o.route_line_id:
                    raise osv.except_osv(_('Invalid action !'), 
                            _('Cannot update a Picking(s) which are already delivery routed (%s) !'%o.route_id.name))
        return  super(stock_picking, self).write(cr, uid, ids, vals, context=context)

    
    def unlink(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.route_line_id:
                self.pool.get('delivery.route.line').unlink(cr,uid,[o.route_line_id.id],context=context)
        return super(stock_picking, self).unlink(cr, uid, ids, context=context)
        
stock_picking()
