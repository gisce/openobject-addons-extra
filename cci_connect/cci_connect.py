# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 CCI Connect ASBL. (http://www.cciconnect.be) All Rights Reserved.
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

import time
from osv import fields, osv

class delayed_partner(osv.osv):
    _name = "cci_connect.delayed_partner"
    _description = "store asked changes for partner and address from internet site"
    _columns = {
        'partner_id' : fields.many2one('res.partner','Partner',required=True),
        'address_id' : fields.many2one('res.partner.address','Address',required=True),
        'partner_name' : fields.char('Name', size=128 ),
        'partner_title' : fields.char('Title', size=16, translate=True),
        'website': fields.char('Website',size=64),
        'vat': fields.char('VAT',size=32),
        'searching' : fields.text('Searching'),
        'selling' : fields.text('Selling'),
        'address_name': fields.char('Address Name', size=64),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip_id':fields.many2one('res.partner.zip','Zip'),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('Site E-Mail', size=240),
        'phone': fields.char('Site Phone', size=64),
        'fax': fields.char('Site Fax', size=64),
        'asker_id' : fields.many2one('res.partner.contact','Asker for Change'),
        'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Canceled')],'State'),
        'state_changed': fields.date('Status Changed'),
        'final_partner_name' : fields.char('Final Partner Name', size=128 ),
        'final_partner_title' : fields.char('Final Title', size=16, translate=True),
        'final_website': fields.char('Final Website',size=64),
        'final_vat': fields.char('Final VAT',size=32),
        'final_searching' : fields.text('Final Searching'),
        'final_selling' : fields.text('Final Selling'),
        'final_address_name': fields.char('Final Address Name', size=64),
        'final_street': fields.char('Final Street', size=128),
        'final_street2': fields.char('Final Street2', size=128),
        'final_zip_id':fields.many2one('res.partner.zip','Final Zip'),
        'final_country_id': fields.many2one('res.country', 'Final Country'),
        'final_email': fields.char('Final Site E-Mail', size=240),
        'final_phone': fields.char('Final Site Phone', size=64),
        'final_fax': fields.char('Final Site Fax', size=64),
    }
delayed_partner()

