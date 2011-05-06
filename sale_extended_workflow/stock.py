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


class stock_picking(osv.osv):
    
    _inherit = "stock.picking"
    
    def create(self, cr, uid, vals, context=None):
        picking_id = super(stock_picking, self).create(cr, uid, vals, context)
        if vals.get('sale_id', False) and self.pool.get('sale.order').search(cr, uid, [['reserved', '=', True], ['id', '=', vals['sale_id']]], context=context):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_reserve', cr)
        return picking_id

stock_picking()
