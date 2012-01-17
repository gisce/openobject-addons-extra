# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale layout cleanup module for OpenERP
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
    'name': 'Sale layout cleanup module',
    'version': '1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """This module cleans up the implementation of the module 'sale_layout' currently available in the addons.
It allows an easy and clean use of sale_layout with aeroo reports and other modern reporting engines. The main innovation of this module is that the sale order report with layout doesn't use the parser any more i.e. the file addons/sale_layout/report/report_sale_layout.py is not used any more.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale_layout'],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
