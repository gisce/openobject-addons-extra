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

from osv import osv, fields
from tools.translate import _

class country_state(osv.osv):
    _inherit = 'res.country.state'
    _description = 'Country States'
    _columns = {
        'province_ids': fields.one2many('res.country.province', 'state_id', 'Provinces'),
    }

country_state()

class country_province(osv.osv):
    _name = 'res.country.province'
    _description = 'Country State Provinces'
    _columns = {
            'state_id': fields.many2one('res.country.state', 'State', required=True),
            'name': fields.char('Province Name', size=64, required=True),
            'code': fields.char('Province Code', size=6, required=True),
            'district_ids': fields.one2many('res.country.district', 'province_id', 'Districts'),
        }
    _sql_constraints = [
            ('code_uniq','unique(code)',_('The code of the province must be unique !'))
        ]
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('code', '=', name)] + args, limit=limit,
                context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
country_province()

class country_district(osv.osv):
    _name = 'res.country.district'
    _description = 'Country State Province Districts'
    _columns = {
            'province_id': fields.many2one('res.country.province', 'Province', required=True),
            'name': fields.char('District Name', size=64, required=True),
            'code': fields.char('District Code', size=8, required=True),
        }
    _sql_constraints = [
            ('code_uniq','unique(code)',_('The code of the district must be unique !'))
        ]

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('code', '=', name)] + args, limit=limit,
                context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
        
country_district()
