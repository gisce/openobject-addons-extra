# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
# Copyright (c) 2012 Cubic ERP - Teradata SAC. (http://cubicerp.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    _columns = {
            'natural_person': fields.boolean('Natural Person', size=32),
            'first_name': fields.char('First Name', size=32),
            'middle_name': fields.char('Middle Name', size=32),
            'surname': fields.char('Surname', size=32),
            'mother_name': fields.char("Mother's Name", size=32)
        }
        
    _default = {
            'natural_person': False,
        }

    def onchange_natural_person(self, cr, uid, ids, value, first_name, middle_name, surname, mother_name, context=None):
        name = ''
        if value:
            name = (first_name and (first_name+' ') or '') + (middle_name and (middle_name+' ') or '') + (surname and (surname+' ') or '') + (mother_name and (mother_name+' ') or '')
        return {'value':{'name':name}}

    def onchange_person_name(self, cr, uid, ids, first_name, middle_name, surname, mother_name, context=None):
        res = {'value':{}}
        res['value']['name'] = (first_name and (first_name+' ') or '') + (middle_name and (middle_name+' ') or '') + (surname and (surname+' ') or '') + (mother_name and (mother_name+' ') or '')
        return res

    def vat_change(self, cr, uid, ids, value, context=None):
        res = super(res_partner,self).vat_change(cr, uid, ids, value, context=context)
        if len(str(value)) > 2:
            res['value']['ref'] = value[2:]
        return res

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
