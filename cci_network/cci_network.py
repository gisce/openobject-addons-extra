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
# Version 5.0.1 : Philmer

from osv import fields, osv

class network_license(osv.osv):
    _name = "network.license"
    _description = "A bundle of licenses"
    _columns = {
        'name': fields.char('Name',size=100),
        'count': fields.integer('Number of licenses in this bundle'),
        'unit_cost': fields.float('Cost by unit'),
        'note': fields.text('Note'),
        'date' : fields.date('Purchase Date'),
        'validity' : fields.date('Valid until'),
        'supplier_id': fields.many2one('res.partner','Supplier'),
        'invoice_id': fields.many2one('account.invoice','Invoice'),
        'software_ids': fields.one2many('network.software','license_id','Software using'),
        'source_license_id': fields.many2one('network.license','Source License'),
    }
    _defaults = {
        'count' : lambda *a : 1,
    }
network_license()

class network_software(osv.osv):
    _inherit = 'network.software'
    _description = 'Software installed on machine'
    _columns = {
        'license_id': fields.many2one('network.license','Used license'),
    }
network_software()

class network_material(osv.osv):
    _inherit = 'network.material'
    _description = 'Network.Material'
    _columns = {
        'active': fields.boolean('Active'),
        'current_user_id': fields.many2one('res.users','Current User'),
        'cost': fields.float('Cost'),
        'invoice_id': fields.many2one('account.invoice','Invoice'),
        'planned_replacement': fields.date('Planned Replacement Date'),
    }
    _defaults = {
        'active' : lambda *a : True,
    }
network_material()
