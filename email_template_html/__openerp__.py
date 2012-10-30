# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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
    "name": "E-Mail Templates Body Rich",
    "author": "OpenERP SA",
    'complexity': "easy",
    "version": "0.1",
    "depends": ["email_template"],
    "category": "Hidden",
    "description": """
    The module will add the Option `Use Body Rich/HTML ?` on Mail Compose Wizard
It gives priority to the HTML type Mail if we have HTML Body. Also While Replying
Mail if mail has Subtype HTML it allows Send HTML format reply.
    """,
    "init_xml": [],
    "update_xml": [
        'wizard/email_compose_message_view.xml',
    ],
    "demo_xml": [],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
