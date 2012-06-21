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

{
    "name" : "Perú Localización - Topónimos", 
    "version" : "1.0",
    "author" : "Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Localization",
    "description": """
Adds Region, Province, District and locality of Perú
    """,
    "depends" : ["base"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'res_country_view.xml',
        'partner_view.xml',
        'res_country_data.xml',
        "security/ir.model.access.csv",
        ],
    'installable' : True,
    'active' : False,
}
