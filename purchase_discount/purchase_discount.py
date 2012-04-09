##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import osv,fields
import decimal_precision as dp

class purchase_order_line(osv.osv):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, line.price_unit * line.product_qty * (1 - (line.discount or 0.0) /100.0))
        return res

    _columns = {
        'discount': fields.float('Discount (%)', digits=(16,2)),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
    }

    _defaults = {
        'discount': lambda *a: 0.0,
    }
    
purchase_order_line()

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                for c in self.pool.get('account.tax').compute(cr, uid, line.taxes_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_qty, order.partner_address_id.id, line.product_id, order.partner_id):
                    val += c['amount']
                val1 += line.price_subtotal
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),
    }

purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

