# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Account General Ledger",
    "version" : "1.1",
    "author" : "OpenERP SA",
    "category": 'Accounting & Finance',
    'complexity': "easy",
    "description": """
Account General Ledger.
====================================
This module is used for managing the ledger reports of different accounts. It manages the generation of reports of 
different accounts on the basis of the entries in those accounts. The reports can be also generated either in 
landscape mode or without landscape mode. It also helps to reports either by filtering or without filtering. 
If user wants to print reports using filter then the filtering of accounts can be done by date and also 
by periods. 

The greatest functionality about this module which is provided by OpnERP is that user can print the reports 
from general ledger of the selected accounts. If the user wants to generate reports of some selected 
accounts only then the accounts should be selected from Accounts to include. So that the reports of the selected 
accounts can be generated otherwise the reports of all accounts will also be generated.    
    """,
    'website': 'http://www.openerp.com',
    'images' : [],
    'init_xml': [],
    "depends" : ["account"],
    'update_xml': [
        'wizard/wizard_account_general_ledger_view.xml',
        'account_general_ledger_report.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: