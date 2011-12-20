#-*- coding: utf-8 -*-
'''
Created on 19 déc. 2011

@author: openerp
'''
from osv import fields, osv

class document_directory_type(osv.osv):
    _name = 'document.directory.type'
    
    _columns = {
        'name': fields.char('Directory Type', size=64)
    }
    
class document_change_type(osv.osv):
    _name = "document.change.type"
    _description = "Document Type"
    _columns = {
        'name': fields.char("Document Type", size=64,required=True),
        'code' : fields.char("ISO Code", size=64),
        'directory_type_id' :fields.many2one('document.directory.type','Directory Type', help='This link allow to define on wich kind of directory this type of document is attached with'),
        'template_document_id':fields.many2one('ir.attachment','Template Document'),
        'sequence' : fields.integer('Sequence Number',  help="Allow to define order for documents"),
    }
    
    _order = "sequence asc"
    
class document_change_process_type(osv.osv):
    _name = "document.change.process.type"
    _description = "Process Type"
    _columns = {
        'name': fields.char("Process Type", size=64),
        'document_type_ids' : fields.many2many('document.change.type','document_type_process_type_rel','process_change_type_id','document_type_id','Document Type')
    }
    
    
class process_change_stage(osv.osv):
    _name = "cat.process_change.stage"
    
    _columns = {
            'name' : fields.char("Name", size=128),
            'sequence' : fields.integer('Sequence Number', help="Allow to define order for stages"),
    }
    
    
    
