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


{
    'name': 'Sale partner bank',
    'version': '1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """This modules adds a 'Bank account' field on partners and sale orders. This field is copied from partner to sale order and then from sale order to customer invoice.

This module is similar to the 'sale_payment' module ; the main difference is that it doesn't have any extra-dependancy i.e. it doesn't depend on the 'account_payment_extension' module.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale'],
    'init_xml': [],
    'update_xml': [
        'sale_view.xml',
        'partner_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
