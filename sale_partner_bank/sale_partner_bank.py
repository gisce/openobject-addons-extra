# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale partner bank module for OpenERP
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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'partner_bank_id': fields.many2one('res.partner.bank','Bank account', select=True, help='Select the bank account on which the customer should pay. This field will be copied to the sale order and from there to the customer invoice.'),
        }


class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'partner_bank_id': fields.many2one('res.partner.bank','Bank account', select=True, help='Select the bank account on which the customer should pay. This field is copied from the partner form and will be copied to the customer invoice.'),
        }

    def onchange_partner_id(self, cr, uid, ids, part):
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        if part:
            partner = self.pool.get('res.partner').read(cr, uid, part, ['partner_bank_id'])
            if partner:
                result['value'].update({'partner_bank_id': partner['partner_bank_id']})
        return result

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None):
# We must return a unique ID !!!
        invoice_id = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped=grouped, states=states, date_inv=date_inv, context=context)
        cur_sale_order = self.pool.get('sale.order').browse(cr, uid, ids[0], context=context)
        self.pool.get('account.invoice').write(cr, uid, invoice_id, {
                'partner_bank_id': cur_sale_order.partner_bank_id.id
            }, context=context)
        return invoice_id


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """Copy bank partner from sale order to invoice"""
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.sale_id:
            invoice_vals.update({'partner_bank_id': picking.sale_id.partner_bank_id.id})
        return invoice_vals

