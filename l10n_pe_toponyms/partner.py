# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import fields, osv

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _name = 'res.partner.address'

    _columns = {
        'province_id': fields.many2one("res.country.province", 'Province', domain="[('state_id','=',state_id)]"),
        'district_id': fields.many2one("res.country.district", 'District', domain="[('province_id','=',province_id)]"),
        'address_ref' : fields.char('Address Reference', size=256, help="One or more points used as reference to locate the address"),
    }

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street','state_id','province_id','district_id','address_ref','street2']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                elems = [r['name'], r['street'], r['street2'], r['district_id'] and r['district_id'][1], r['province_id'] and r['province_id'][1], r['address_ref'] ]
                addr = ', '.join(filter(bool, elems))
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr or '/')))
                else:
                    res.append((r['id'], addr or '/'))
        return res

res_partner_address()

