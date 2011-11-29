# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Stock Picking Organizer module for OpenERP                                 #
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
from tools.translate import _

class stock_picking_organizer_wizard(osv.osv_memory):
    _name = 'stock.picking.organizer.wizard'
    _description = 'stock picking organizer wizard'     

    _columns = {
        'picking_option': fields.selection([('selected', 'Selected Picking'), ('all', 'All Internal Picking')], 'Merge'),
        'number_of_output_picking': fields.integer('Number of Output Picking'),
    }

    _defaults = {
        'picking_option': lambda *a: 'all',
        'number_of_output_picking': lambda *a: 1,
    }
  
    def reorganized_picking(self, cr, uid, id, context):
        #TODO this wizard have to work and used only for the outgoing picking. Add some check
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        wizard = self.browse(cr, uid, id, context=context)[0]
        if wizard.picking_option == 'selected':
            picking_ids = context['active_ids']
            if picking_obj.search(cr, uid, [['id', 'in', picking_ids], ['type', 'in', ['out', 'in']]]):
                raise  osv.except_osv(_('Error !'),_('Incomming or Outgoing picking can not be merge'))
        else:
            #the INT is hardcoded :S not clean at all but in V6 outgoing and delivery picking have no difference :S
            #picking_ids = picking_obj.search(cr, uid, [['state', '=', 'assigned'], ['type', '=', 'out'], ['name', 'ilike', 'INT%']])
            picking_ids = picking_obj.search(cr, uid, [['state', '=', 'assigned'], ['type', '=', 'internal']])

        move_ids =  move_obj.search(cr, uid, [['picking_id', 'in', picking_ids]], context=context)
        
        res = {}
        res2=[]
        for move in move_obj.browse(cr, uid, move_ids, context=context):
            product = move.product_id
            if res.get(product.id, False):
                res[product.id] += [move.id]
            else:
                res[product.id] = [move.id]
                res2 += [(product.loc_rack, product.loc_row, product.id)]

        res2.sort()
        step = int(round(len(res2)/(wizard.number_of_output_picking*1.0) + 0.4999, 0))
        count = 0
        while res2 and count<1000:
            picking_id = picking_obj.create(cr, uid, {'type': 'internal', 'origin':'MERGE'}, context=context)
            move_ids = []
            for val in res2[0:step]:
                move_ids += res[val[2]]
            move_obj.write(cr, uid, move_ids, {'picking_id':picking_id}, context=context)
            res2 = res2[step:]
            count+=1
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        picking_obj.unlink(cr, uid, picking_ids,context=context)

        return {'type': 'ir.actions.act_window_close'}
                
                
stock_picking_organizer_wizard()
