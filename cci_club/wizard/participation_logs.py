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
import pooler

def _select_logs(self, cr, uid, data, context):
    participation_ids = data['ids']
    #cr.execute('SELECT section_id FROM event_event WHERE id = %s', (event_id, ))
    #res = cr.fetchone()
    values = {
        'domain': [('participation_id', 'in', participation_ids)],
        'name': 'Participation Log',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'cci_club.participation_log',
        'context': {},
        'type': 'ir.actions.act_window',
    }
    return values
class wizard_participation_log(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _select_logs,
                'state': 'end'
            }
        },
    }
wizard_participation_log("wizard_cci_club_participation_log")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

