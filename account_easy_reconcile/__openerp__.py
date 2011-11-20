# -*- coding: utf-8 -*-
##############################################################################
#
#    Account easy reconcile module for OpenERP
#    Copyright (C) 2010 -2011 Akretion Sébastien BEAU 
#                                   <sebastien.beau@akretion.com>
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
    "name" : "Account Easy Reconcile",
    "version" : "1.0",
    "depends" : [
            "account",
            "base_scheduler_creator",
                ],
    "author" : "Akretion",
    "description": """A new way to reconcile easily your account
""",
    'license': 'AGPL-3',
    "website" : "http://www.akretion.com/",
    "category" : 'Generic Modules/Accounting',
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["easy_reconcile.xml"],
    "active": False,
    "installable": True,

}
