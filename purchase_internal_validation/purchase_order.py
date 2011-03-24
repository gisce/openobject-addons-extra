# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import netsvc

from osv import osv, fields

class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('waiting_validation', 'Waiting Validation'),
        ('wait', 'Waiting'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    #TODO: implement messages system
    def wkf_wait_validation_order(self, cr, uid, ids, context=None):
        todo = []
        import pdb;pdb.set_trace()
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error !'),_('You can not wait for purchase order to be validated without Purchase Order Lines.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
            message = _("Purchase order '%s' is waiting for validation.") % (po.name,)
            self.log(cr, uid, po.id, message)
#        current_name = self.name_get(cr, uid, ids)[0][1]
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'waiting_validation'})
        return True

purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
