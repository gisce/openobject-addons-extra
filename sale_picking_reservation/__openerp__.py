# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_picking_reservation for OpenERP                                       #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################


{
    'name': 'sale_picking_reservation',
    'version': '0.2',
    'category': 'Generic Modules',
    'license': 'AGPL-3',
    'description': """This module add the possibility to reserve the product of the quotation line before validating the sale order.""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['sale'], 
    'init_xml': [],
    'update_xml': [ 
           'sale_workflow.xml',
           'sale_view.xml',
           'stock_workflow.xml',
           'stock_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

