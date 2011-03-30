# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import netsvc
import wizard
import netsvc
import os

_result_form = '''<?xml version="1.0"?>
<form string="Get Emails List">
    <separator string="Emails" colspan="4"/>
    <field name="chained_emails" widget="text" colspan="4" nolabel="1"/>
    <label string="This list is placed is the clipboard. You can paste it with a Ctrl-C in your regular email client." colspan="4"/>
</form>'''

_fields = {
    'chained_emails': {'string':'List', 'type':'char','readonly':True},
}

def _get_result(self, cr, uid, data, context):
    service = netsvc.LocalService("object_proxy")
    res = service.execute(cr.dbname, uid, 'cci_club.participation', 'read', data['ids'], ['email'])
    emails = []
    for r in res:
        if r['email'] and not r['email'] in emails:
            emails.append( r['email'] )
    if os.name == 'nt':
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData( win32clipboard.CF_TEXT, ';'.join(emails) )
        win32clipboard.CloseClipboard()
    elif os.name == 'posix':
        import pygtk
        pygtk.require('2.0')
        import gtk
        clipboard = gtk.clipboard_get()
        clipboard.set_text( '; '.join(emails) )
        clipboard.store()
    return {'chained_emails':'; '.join(emails)}

class get_emails_list(wizard.interface):
    states = {
        'init': {
            'actions': [_get_result],
            'result': {'type': 'form', 'arch':_result_form, 'fields': _fields, 'state':[('end','Ok')]}
        },
    }
get_emails_list('cci_club.get_emails_list')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

