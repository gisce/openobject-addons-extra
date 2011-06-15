# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import wizard
import osv
import pooler

intro_stop_form = '''<?xml version="1.0"?>
<form string="Module Recording">
    <separator string="Recording Information" colspan="4"/>
    <label string="Open ERP recording is stopped. Don't forget to save the recorded module." colspan="4" align="0.0"/>
    <label string="You can continue the recording session by relauching the 'start recording' wizard." colspan="4" align="0.0"/>
</form>'''

intro_start_form = '''<?xml version="1.0"?>
<form string="Recording Stopped">
    <separator string="Recording information" colspan="4"/>
    <label string="The module recorder allows you to record every operation made in the Open ERP client and save them as a module. You will be able to install this module on any database to reuse and/or publish it." colspan="4" align="0.0"/>
    <field name="continue"/>
</form>'''

intro_start_fields = {
    'continue': {'string':'Continue Previous Session', 'type':'boolean'}
}

def _stop_recording(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    mod = pool.get('ir.module.record')
    mod.recording = 0
    return {}

def _start_recording(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    mod = pool.get('ir.module.record')
    mod.recording = 1
    if not data['form']['continue']:
        mod.recording_data = []
        mod.depends = {}
    return {}

def _check_recording(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    mod = pool.get('ir.module.record')
    if mod.recording:
        return 'stop'
    return 'start'

class base_module_publish(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type':'choice',
                'next_state':_check_recording,
            }
        },
        'start': {
            'actions': [],
            'result': {
                'type':'form',
                'arch':intro_start_form,
                'fields': intro_start_fields,
                'state':[
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start_confirm', 'Start Recording', 'gtk-ok'),
                ]
            }
        },
        'start_confirm': {
            'actions': [_start_recording],
            'result': {
                'type':'state',
                'state': 'end'
            }
        },
        'stop': {
            'actions': [_stop_recording],
            'result': {
                'type':'form',
                'arch':intro_stop_form,
                'fields': {},
                'state':[
                    ('end', 'Continue', 'gtk-ok'),
                ]
            }
        }
    }
base_module_publish('base_module_recorder.module_record')

# Instead of inheriting from the normal object_proxy class, we inherit
# from whatever class is currently used. Otherwise we would highjack
# the current service.
objects_proxy = netsvc.ExportService.getService('object_proxy').__class__

class recording_objects_proxy(objects_proxy):
    def execute(self, *args, **argv):
        if args[3] == 'create':
            _old_args = args[4].copy()
        elif args[3] == 'write':
            _old_args = args[5].copy()
        elif len(args) >= 5 and isinstance(args[4], dict):
            _old_args = args[4].copy()
        elif len(args) > 5 and args[3] != 'write' and isinstance(args[5], dict):
            _old_args = args[5].copy()
        else:
            _old_args = None
        res = super(recording_objects_proxy, self).execute(*args, **argv)
        pool = pooler.get_pool(args[0])
        mod = pool.get('ir.module.record')

        if mod and mod.recording:
            if args[3] not in ('default_get','read','fields_view_get','fields_get','search','search_count','name_search','name_get','get','request_get', 'get_sc', 'unlink'):
                if _old_args is not None:
                    if args[3] != 'write' and args[3] != 'create' and len(args) > 5 and isinstance(args[5], dict):
                       args=list(args) 
                       args[5]=_old_args
                       args=tuple(args)
                       mod.recording_data.append(('osv_memory_action', args, argv ,None))
                    else:
                       if args[3] == 'create':
                           args[4].update(_old_args)
                       elif args[3] == 'write':
                           args[5].update(_old_args)
                       mod.recording_data.append(('query', args, argv,res))
        return res

    def exec_workflow(self, *args, **argv):
        res = super(recording_objects_proxy, self).exec_workflow(*args, **argv)
        pool = pooler.get_pool(args[0])
        mod = pool.get('ir.module.record')
        if mod and mod.recording:
            mod.recording_data.append(('workflow', args, argv))
        return res

recording_objects_proxy()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

