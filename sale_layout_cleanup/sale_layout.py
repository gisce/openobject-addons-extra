# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale layout cleanup module for OpenERP
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
import decimal_precision as dp

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    # add "id asc", so that the position of subtotal line in the report is
    # fully predictable
    _order = "order_id, sequence asc, id asc"

    def _compute_layout_subtotal(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for subtotal_id in ids:
            result[subtotal_id] = 0.0
            cur_ol = self.read(cr, uid, subtotal_id, ['order_id', 'sequence', 'layout_type'], context=context)
            # Don't compute the subtotal value if it's not a subtotal line
            if cur_ol['layout_type'] <> 'subtotal':
                continue
            # WARNING : the _order on sale_order_line should be :
            # _order = "order_id, sequence asc, id asc"
            # on the native sale_layout, it lacks "id asc"
            # Seach sale order lines of the same sale order with sequence < my_sequence
            # Important : sort the result by ascending sequence, then ID, like it's done in the
            # report
            ids_line_inf_seq_ordered = self.search(cr, uid, [('order_id', '=', cur_ol['order_id'][0]),
                ('sequence', '<', cur_ol['sequence'])], order="sequence asc, id asc", context=context)
            # Seach sale order lines of the same sale order with sequence = my_sequence
            # but ID < my ID, and I sort the result by ID, like it's done in the report
            ids_line_same_seq_above_ordered = self.search(cr, uid, [('order_id', '=', cur_ol['order_id'][0]),
                ('sequence', '=', cur_ol['sequence']), ('id', '<', subtotal_id)], order="id asc", context=context)
            # So, if I add the result of the 2 searches, I get all the sale order lines
            # that are above the subtotal line in the report, IN THE ORDER OF THE REPORT !
            # I reverse the result, then sum the "price_subtotal" of the "article" lines
            # until we reach a "subtotal" line (which is in fact the previous subtotal line in
            # the report)
            ids_line_above_reverse_ordered = []
            ids_line_above_reverse_ordered.extend(ids_line_inf_seq_ordered)
            ids_line_above_reverse_ordered.extend(ids_line_same_seq_above_ordered)
            ids_line_above_reverse_ordered.reverse()

            for cur_id in ids_line_above_reverse_ordered:
                read_cur_id = self.read(cr, uid, cur_id, ['layout_type', 'price_subtotal'], context=context)
                # when we reach the "subtotal" line the closest above us, we stop the sum !
                if read_cur_id['layout_type'] == 'subtotal':
                    break
                if read_cur_id['layout_type'] == 'article':
                    result[subtotal_id] += read_cur_id['price_subtotal']
        return result


    _columns = {
        'layout_subtotal': fields.function(_compute_layout_subtotal, string='Layout subtotal', digits_compute=dp.get_precision('Sale Price')),
        # We remove "Page break" in 'layout_type' because I haven't found a way to
        # implement "Page break" with Aeroo reports
        'layout_type': fields.selection([
                ('article', 'Product'),
                ('title', 'Title'),
                ('text', 'Note'),
                ('subtotal', 'Sub Total'),
                ('line', 'Separator Line'),
            ],'Line Type', select=True, required=True),
    }

sale_order_line()


