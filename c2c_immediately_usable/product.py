# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
from tools.translate import _

class ProductImmediatelyUsable(osv.osv):
    """
    Inherit Product in order to add an "immediately usable quantity" stock field
    """
    
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        # We need available and outgoing quantities to compute immediately usable
        # quantity so we add them in the calculation
        if 'immediately_usable_qty' in field_names:
            field_names.append('qty_available')
            field_names.append('outgoing_qty')
            
        res = super(ProductImmediatelyUsable, self)._product_available(cr, uid, ids, field_names, arg, context)
        
        if 'immediately_usable_qty' in field_names:        
            for product_id, stock_qty in res.iteritems():
                res[product_id]['immediately_usable_qty'] = stock_qty['qty_available'] - stock_qty['outgoing_qty']
        
        return res
    
    _inherit = 'product.product'
    _columns = {
        'qty_available': fields.function(_product_available, method=True, type='float', string='Real Stock', help="Current quantities of products in selected locations or all internal if none have been selected.", multi='qty_available'),
        'virtual_available': fields.function(_product_available, method=True, type='float', string='Virtual Stock', help="Futur stock for this product according to the selected location or all internal if none have been selected. Computed as: Real Stock - Outgoing + Incoming.", multi='qty_available'),
        'incoming_qty': fields.function(_product_available, method=True, type='float', string='Incoming', help="Quantities of products that are planned to arrive in selected locations or all internal if none have been selected.", multi='qty_available'),
        'outgoing_qty': fields.function(_product_available, method=True, type='float', string='Outgoing', help="Quantities of products that are planned to leave in selected locations or all internal if none have been selected.", multi='qty_available'),    
        'immediately_usable_qty': fields.function(_product_available, method=True, type='float', string='Immediately Usable Stock', help="Quantities of products really available for sale. Computed as: Real Stock - Outgoing.", multi='qty_available'),
    }
    
    
ProductImmediatelyUsable()
