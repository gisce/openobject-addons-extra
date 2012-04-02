# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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

from osv import osv
from tools.translate import _
from merge_external_referential import ExtRefMerger

class base_partner_merge_address_values(osv.osv_memory, ExtRefMerger):
    """
    Merges two partners. Adaptations for base_external_referentials
    """
    _inherit = 'base.partner.merge.address.values'

    _merge_model = 'res.partner.address'

    def check_addresses(self, cr, uid, add_data, context):
        """
         Check validity of selected addresses.
         Hook for other checks
        """
        super(base_partner_merge_address_values, self).check_addresses(cr, uid, add_data, context)
        if self.has_an_external_ref(cr, uid, add_data.address_id1.id, context=context) and \
           self.has_an_external_ref(cr, uid, add_data.address_id2.id, context=context):
            raise osv.except_osv(_('Error!'), _('You cannot merge 2 addresses which are both linked with an external referential!'))
        return True

    def custom_updates(self, cr, uid, address_id, old_address_ids, context):
        """
        Hook for special updates on old addresses and new address
        Update ir_model_data references to external referentials
        """
        old_address_ids = old_address_ids or []
        return self.update_external_refs(
            cr, uid, address_id, old_address_ids, context=context)

base_partner_merge_address_values()
