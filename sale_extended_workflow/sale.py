# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_extended_workflow for OpenERP                                          #
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

    def action_reserve(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'reserved': True})
        self.action_ship_create(cr, uid, ids, *args)
        return True

    def action_unreserve(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'reserved': False})
        for sale in self.browse(cr, uid, ids):
            for picking in sale.picking_ids:
                picking.unlink()
        return True

    def action_ship_create(self, cr, uid, ids, *args):
        sale_order_reserved_ids = self.search(cr, uid, [['reserved', '=', True], ['id', 'in', ids], ['picking_ids','!=',False]])
        sale_order_to_confirm_ids = [x for x in ids if x not in sale_order_reserved_ids]
        wf_service = netsvc.LocalService("workflow")
        for sale in self.read(cr, uid, sale_order_reserved_ids, ['picking_ids']):
            for picking_id in sale['picking_ids']:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm_reserved', cr)
        return super(sale_order, self).action_ship_create(cr, uid, sale_order_to_confirm_ids, *args)





sale_order()
