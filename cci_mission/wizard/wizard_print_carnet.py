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
import time
import pooler


form1 = """<?xml version="1.0"?>
<form string="Select No. of Header Pages">
    <field name="header"/>
</form>"""
fields1 = {
    'header': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 1},
}

form2 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Exportation">
    <field name="export"/>
</form>"""
fields2 = {
    'export': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 4},
}

form3 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Importation">
    <field name="import"/>
</form>"""
fields3 = {
    'import': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 4},
}

form4 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Transit">
    <field name="transit"/>
</form>"""
fields4 = {
    'transit': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 20},
}

form5 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Re-Exportation">
    <field name="reexport"/>
</form>"""
fields5 = {
    'reexport': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 4},
}

form6 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Re-Importation">
    <field name="reimport"/>
</form>"""
fields6 = {
    'reimport': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 4},
}

form7 = """<?xml version="1.0"?>
<form string="Select No. of Pages for Certificate of Presence">
    <field name="presence"/>
</form>"""
fields7 = {
    'presence': {'string': 'No. of pages', 'type':'integer', 'default':lambda *a : 4},
}

form8 = """<?xml version="1.0"?>
<form string="Select No. of Voucher export/re-importation">
    <field name="export_reimport"/>
</form>"""
fields8 = {
    'export_reimport': {'string': 'No. of voucher', 'type':'integer', 'default':lambda *a : 4},
}

form9 = """<?xml version="1.0"?>
<form string="Select No. of Voucher import/re-exportation">
    <field name="import_reexport"/>
</form>"""
fields9 = {
    'import_reexport': {'string': 'No. of voucher', 'type':'integer', 'default':lambda *a : 4},
}

form10 = """<?xml version="1.0"?>
<form string="Select No. of Voucher Transit">
    <field name="vtransit"/>
</form>"""
fields10 = {
    'vtransit': {'string': 'No. of voucher', 'type':'integer', 'default':lambda *a : 5},
}

class wizard_report(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form1, 'fields':fields1, 'state':[('ask2','Skip'),('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet1', 'state':'ask2'},
        },
        'ask2': {
            'actions': [],
            'result': {'type':'form', 'arch':form2, 'fields':fields2, 'state':[('init','Preceding once again'),('ask3','Skip'),('end','Cancel'),('print2','Print')]},
        },
        'print2': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet2', 'state':'ask3'},
        },
        'ask3': {
            'actions': [],
            'result': {'type':'form', 'arch':form3, 'fields':fields3, 'state':[('ask2','Preceding once again'),('ask4','Skip'),('end','Cancel'),('print3','Print')]},
        },
        'print3': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet3', 'state':'ask4'},
        },
        'ask4': {
            'actions': [],
            'result': {'type':'form', 'arch':form4, 'fields':fields4, 'state':[('ask3','Preceding once again'),('ask5','Skip'),('end','Cancel'),('print4','Print')]},
        },
        'print4': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet4', 'state':'ask5'},
        },
        'ask5': {
            'actions': [],
            'result': {'type':'form', 'arch':form5, 'fields':fields5, 'state':[('ask4','Preceding once again'),('ask6','Skip'),('end','Cancel'),('print5','Print')]},
        },
        'print5': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet5', 'state':'ask6'},
        },
        'ask6': {
            'actions': [],
            'result': {'type':'form', 'arch':form6, 'fields':fields6, 'state':[('ask5','Preceding once again'),('ask7','Skip'),('end','Cancel'),('print6','Print')]},
        },
        'print6': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet6', 'state':'ask7'},
        },
        'ask7': {
            'actions': [],
            'result': {'type':'form', 'arch':form7, 'fields':fields7, 'state':[('ask6','Preceding once again'),('ask8','Skip'),('end','Cancel'),('print7','Print')]},
        },
        'print7': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet7', 'state':'ask8'},
        },
        'ask8': {
            'actions': [],
            'result': {'type':'form', 'arch':form8, 'fields':fields8, 'state':[('ask7','Preceding once again'),('ask9','Skip'),('end','Cancel'),('print8','Print')]},
        },
        'print8': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet8', 'state':'ask9'},
        },
        'ask9': {
            'actions': [],
            'result': {'type':'form', 'arch':form9, 'fields':fields9, 'state':[('ask8','Preceding once again'),('ask10','Skip'),('end','Cancel'),('print9','Print')]},
        },
        'print9': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet9', 'state':'ask10'},
        },
        'ask10': {
            'actions': [],
            'result': {'type':'form', 'arch':form10, 'fields':fields10, 'state':[('ask9','Preceding once again'),('end','Skip'),('end','Cancel'),('print10','Print')]},
        },
        'print10': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet10', 'state':'end'},
        },
    }

wizard_report('cci_missions_print_carnet')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

