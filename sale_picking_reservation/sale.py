# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_picking_reservation for OpenERP                                       #
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


class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'reserved': fields.boolean('Reserved Sale Order', readonly=True),
    }

    _defaults = {
        'reserved': lambda *a: False,
    }


    def copy(self, cr, uid, id, default=None, context=None):
        """Don't mark copied orders reserved"""
        if default is None:
            default = {}
        else:
            default = default.copy()
        default['reserved'] = False
        return super(sale_order, self).copy(cr, uid, id, default, context=context)


    def _prepare_order_picking(self, cr, uid, order, context=None, *args):
        """Prepare data for a reserved picking if the context requires it"""
        res = super(sale_order, self)._prepare_order_picking(cr, uid, order, *args)
        if context and context.get('reserved', False):
            res['reserved'] = True
        return res

    def action_reserve(self, cr, uid, ids, *args):
        """Reserve the goods"""
        self.action_ship_create(cr, uid, ids, {'reserved': True})
        self.write(cr, uid, ids, {'reserved': True})
        return True

    def action_unreserve(self, cr, uid, ids, *args):
        """Cancel the reservation"""
        wf_service = netsvc.LocalService("workflow")
        self.write(cr, uid, ids, {'reserved': False})
        for sale in self.browse(cr, uid, ids):
            # Cancel the picking (deleting it would not cancel the procurements!)
            for picking in sale.picking_ids:
                wf_service.trg_validate(uid, 'stock.picking', picking.id,
                                        'button_cancel', cr)
            # Cancel the procurements
            for move in sale.order_line:
                if move.procurement_id:
                    # Check that canceling the picking raised procurement exceptions
                    wf_service.trg_validate(uid, 'procurement.order', 
                                            move.procurement_id.id,
                                            'button_check', cr)
                    # Cancel the procurement
                    wf_service.trg_validate(uid, 'procurement.order', 
                                            move.procurement_id.id,
                                            'button_cancel', cr)
        return True

    def action_ship_create(self, cr, uid, ids, *args):
        """Confirm reservations pickings, and create them when no reservation was made"""
        sale_order_reserved_ids = self.search(cr, uid, [['reserved', '=', True], ['id', 'in', ids], ['picking_ids','!=',False]])
        wf_service = netsvc.LocalService("workflow")
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        # Mark the orders not reserved
        self.write(cr, uid, sale_order_reserved_ids, {'reserved' : False})
        # Confirm reservations
        for sale in self.read(cr, uid, sale_order_reserved_ids, ['picking_ids']):
            picking_obj.write(cr, uid, sale['picking_ids'], {'reserved' : False})
            move_ids = move_obj.search(cr, uid, [('picking_id', 'in', sale['picking_ids'])])
            move_obj.write(cr, uid, move_ids, {'state':'draft'})
            for picking_id in sale['picking_ids']:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm_reserved', cr)
        # Confirm other orders the standard way
        sale_order_to_confirm_ids = [x for x in ids if x not in sale_order_reserved_ids]
        return super(sale_order, self).action_ship_create(cr, uid, sale_order_to_confirm_ids, *args)

sale_order()
