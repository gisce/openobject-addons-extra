# -*- encoding: utf-8 -*-
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
from osv import osv, fields


class res_partner_team(osv.osv):
    _name = 'res.partner.team'

    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=True),
        'description' : fields.text('Description'),
    }


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'

    _columns = {
        # provide a backwards compatible alias for getting the address info from the "job" object, which in
        # 6.1 was changed from res.partner.job to res.partner.address
        'address_id' : fields.related('location_id', type='many2one',
                                      relation='res.partner.location',
                                      string='Location', store=True),

        # extra fields
        'team_id' : fields.many2one('res.partner.team', 'Team'),
    }
