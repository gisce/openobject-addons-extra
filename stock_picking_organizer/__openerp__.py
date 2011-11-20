# -*- encoding: utf-8 -*-
##############################################################################
#
#    Model module for OpenERP
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
    'name': 'Stock Picking Organizer',
    'version': '0.1',
    'category': 'Generic Modules/Inventory Control',
    'license': 'AGPL-3',
    'description': """Module to merge and split picking. Very usefull when you use OpenERP with the option "Picking List & Delivery Order" """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['sale'],
    'init_xml': [],
    'update_xml': ['stock_picking_organizer.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

