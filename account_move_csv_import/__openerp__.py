# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account move CSV import module for OpenERP
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
    'name': 'Account move CSV import module',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'description': """Imports an account move supplied via a CSV file.
For the moment, it supports :
 - MeilleureGestion.com payroll CSV file
 - LibreOffice CSV export file
but it's a good basis to import other CSV file formats.

Note : One account move per CSV file.

Here are the design guidelines of this module :
- code is easy to read
- code is easy to debug
- expressive error messages
- module with minimum dependancies
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        'import_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
