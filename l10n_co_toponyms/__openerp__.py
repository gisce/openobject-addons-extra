# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Gabriel Henao.
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
    "name": "Colombia Localization Toponyms",
    "version": "1.0",
    "description": """
Colombian toponyms.

Lista de departamentos y municipios colombianos

    """,
    "author": "Gabriel Henao and Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Localization/Toponyms",
    "depends": [
			"base_state_ubication",
			],
	"data":[
        "l10n_states_co_data.xml",
        "l10n_cities_co_data.xml",
			],
    "demo_xml": [
			],
    "update_xml": [
			],
    "active": False,
    "installable": True,
    "certificate" : "",
    "images": [
                        ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
