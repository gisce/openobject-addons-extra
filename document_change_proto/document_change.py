#-*- coding: utf-8 -*-
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

import tools
from osv import fields, osv
import os
import pooler
import netsvc
from tools.translate import _
import time
import datetime
import base64




class document_directory(osv.osv):
    _inherit = 'document.directory'
    _columns = {
        'type_id': fields.many2one('document.directory.type', 'Type'),
        'version' : fields.integer('Version')
    }





class document_change_process(osv.osv):
    _name = "document.change.process"
    _description = "Process"

    def _latestmodification(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        #TODOto calculate latest modified date from all related documents
        return res

    def _get_document(self, cr, uid, ids, context={}, *arg):
        if not ids:
            return {}
        res = {}
        attach = self.pool.get('ir.attachment')
        directory_obj = self.pool.get('document.directory')
        for process_change in self.browse(cr, uid, ids):
            res1 = []
            for phase_id in  process_change.process_phase_ids:
                res1 += map(lambda x:x.id, phase_id.phase_document_ids or [])
            res[process_change.id] = res1
        return res

    def _get_progress(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        progress = 0.0
        for proc_change in self.browse(cr, uid, ids):
            update_docs = []
            result[proc_change.id] = 0.0
            for doc in proc_change.process_document_ids:
                if doc.state in ('to_update', 'change_propose'):
                    update_docs.append(doc)
                progress = (float(len(update_docs))/float(len(proc_change.process_document_ids)))*100
                result[proc_change.id] = progress
        return result

    def _get_current_phase(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for proc in self.browse(cr, uid, ids):
            result[proc.id] = False
            for phase in proc.process_phase_ids:
                if phase.state in ('in_process','to_validate'):
                    result[proc.id] = phase.id
        return result

    _columns = {
        'name': fields.char("Process ID", size=64, required=True, select=True),
        'process_type_id' :fields.many2one('document.change.process.type','Type of Change'),
        'description': fields.char("Title", size=64, required=True),
        'change_description':fields.text('Changed Description'),
        'directory_ids' :fields.many2many('document.directory','directory_process_rel','directory_id','process_id','Directory involved'),
        'user_id':fields.many2one('res.users','Owner',required=True),
        'create_date':fields.datetime('Creation',readonly=True),
        'latest_modified_date':fields.function(_latestmodification, method=True, type='datetime', string="Lastest Modification"), #TODO no year!
        'date_expected':fields.datetime('Expected Production'),
        'date_production':fields.datetime('Real Production'),
        'black_belt': fields.boolean("Black Belt Lead"),
        'need_validation': fields.boolean("Validation Needed"),
        'state':fields.selection([('draft', 'Draft'),('in_progress', 'In Progress'),('to_validate', 'To Validate'), ('pending', 'Pending'), ('done', 'Released'),('cancel','Cancelled')], 'State'),
        'progress': fields.function(_get_progress, method=True, type='float', string='Progress'),
        'process_document_ids': fields.one2many('ir.attachment', 'process_id','Documents To Change'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'document.change.process'),
        'state': 'draft',
        'user_id': lambda laurence,henrion,est,cool: est
      }
    def do_start(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'in_progress'},context=context)
        return True

    def do_pending(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'pending'},context=context)
        return True

    def do_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'to_validate'},context=context)
        return True

    def do_done(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    def do_cancel(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'cancel'},context=context)


class document_file(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
        'change_type_id':fields.many2one('document.change.type','Document Type'),
        'state': fields.selection([('in_production', 'In Production'), ('change_request', 'Change Requested'),('change_propose', 'Change Proposed'), ('to_update', 'To Update'), ('cancel', 'Cancel')], 'State'),
        'target':fields.binary('New Document'),
        'version' : fields.integer('Version'),
        'process_id' : fields.many2one('document.change.process', 'Process change'),
        'date_production':fields.datetime('Real Production'),
    }
    _defaults = {
        'state': lambda *a: 'in_production',
    }

    def _check_duplication(self, cr, uid, vals, ids=[], op='create'):
        name=vals.get('name',False)
        parent_id=vals.get('parent_id',False)
        res_model=vals.get('res_model',False)
        res_id=vals.get('res_id',0)
        type_id=vals.get('change_type_id',False)
        if op=='write':
            for file in self.browse(cr,uid,ids):
                if not name:
                    name=file.name
                if not parent_id:
                    parent_id=file.parent_id and file.parent_id.id or False
                if not res_model:
                    res_model=file.res_model and file.res_model or False
                if not res_id:
                    res_id=file.res_id and file.res_id or 0
                res=self.search(cr,uid,[('id','<>',file.id),('name','=',name),('parent_id','=',parent_id),('res_model','=',res_model),('res_id','=',res_id),('change_type_id','=',type_id)])
                if len(res):
                    return False
        if op=='create':
            res=self.search(cr,uid,[('name','=',name),('parent_id','=',parent_id),('res_id','=',res_id),('res_model','=',res_model),('change_type_id','=',type_id)])
            if len(res):
                return False
        return True

    def button_request(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'change_request'},context=context)
        return True

    def button_propose(self, cr, uid, ids, context={}):
        for attach in self.browse(cr, uid, ids, context=context):
            if not attach.target:
                raise osv.except_osv(_('Error !'), _('You must provide a target content'))
        self.write(cr, uid, ids, {'state':'change_propose'},context=context)
        return True

    def button_validate(self, cr, uid, ids, context={}):
        for attach in self.browse(cr, uid, ids, context=context):
            if not attach.target:
                raise osv.except_osv(_('Error !'), _('You must provide a target content'))
            if (not attach.change_type_id) or not (attach.change_type_id.directory_id.id):
                raise osv.except_osv(_('Configuration Error !'), _('No history directory associated to the document type.'))
            self.copy(cr, uid, [attach.id], {
                'target': False,
                'parent_id': attach.change_type_id.directory_id.id,
                'name': time.strftime('%Y%m%d-%H%M-')+attach.name,
                'datas_fname': time.strftime('%Y%m%d-%H%M-')+attach.datas_fname,
                'state': 'in_production'
            },
            context=context)
            file('/tmp/debug.png','wb+').write(base64.decodestring(attach.target))
            self.write(cr, uid, [attach.id], {
                #'target': False,
                'datas': attach.target,
                'state': 'in_production'
            })
        return True

    def do_production(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'in_production'},context=context)

    def write(self, cr, uid, ids, data, context={}):
        result = super(document_file,self).write(cr,uid,ids,data,context=context)
        return True

    def button_cancel(self, cr, uid, ids, context={}):
        print "cancel"
        return self.write(cr, uid, ids, {'state':'in_production'},context=context)

    def button_draft(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state':'in_production'},context=context)

