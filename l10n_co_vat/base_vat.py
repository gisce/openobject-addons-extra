# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
# Copyright (c) 2011 Cubic ERP - Teradata SAC. (http://cubicerp.com).
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

import string

from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat_co (self,vat ):
        if type(vat) == str:
            vat = vat.replace('-','',1).replace('.','',2)
        if len(str(vat)) < 4:
            return False
        try:
            int(vat)
        except ValueError:
            return False
            
        if len(str(vat)) == 9 and str(vat)[0:5] == '44444' and int(str(vat)[5:]) <= 9000 and int(str(vat)[5:]) >= 4001:
            return True

        nums = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        sum = 0
        RUTLen = len(str(vat))
        for i in range (RUTLen - 2, -1, -1):
            sum += int(str(vat)[i]) * nums [RUTLen - 2 - i]
        if sum % 11 > 1:
            return str(vat)[RUTLen - 1] == str(11 - (sum % 11))
        else:
            return str(vat)[RUTLen - 1] == str(sum % 11)
    
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
