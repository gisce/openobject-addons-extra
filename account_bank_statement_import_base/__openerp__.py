# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    account_bank_statement_import_base for OpenERP                             #
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
    'name': 'account_bank_statement_import_base',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module add some abstraction regarding the bank statement import, The aim is to use the same interface for importing bank statement from various system (paypal, amazon, your personal bank). Also it add some feature of autocompletion.""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['account', 'sale', 'base_scheduler_creator'], 
    'init_xml': [],
    'update_xml': [ 
           'bank_statement_import_view.xml',
           'account_view.xml',
           'partner_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

