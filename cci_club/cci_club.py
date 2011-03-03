# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 CCI Connect ASBL. (http://www.cciconnect.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from osv import fields, osv

class club_type(osv.osv):
    _name = "cci_club.club_type"
    _description = "Type of clubs"
    _columns = {
        'name' : fields.char('Name',size=50,required=True),
    }
club_type()

class level(osv.osv):
    _name = "cci_club.level"
    _description = "Level of knowledge of this participant"
    _columns = {
        'name' : fields.char('Name',size=32,required=True),
        'sequence' : fields.integer('Sequence',required=True),
        'description' : fields.text('Description'),
    }
    _defaults = {
        'sequence': lambda *a: 0,
    }
level()

class club(osv.osv):
    _name = "cci_club.club"
    _description = "Club/Group"
    _columns = {
	    'name' : fields.char('Name',size=128,required=True),
    	'code' : fields.char('Code',size=30),
    	'responsible_id': fields.many2one('res.users', 'Internal club responsible'),
    	'date_begin' : fields.date('Beginning date'),
    	'date_end' : fields.date('End date'),
    	'waiting_club' : fields.boolean('Waiting Club',help='Check this box if this club is not a real club but a club for waiting registrations'),
    	'school_id' : fields.many2one('res.partner','School'),
    	'formative_id' : fields.many2one('res.partner.contact','Formative'),
    	'type_id' : fields.many2one('cci_club.club_type','Type'),
        'description' : fields.text('Description',help='For internal use'),
        'participation_ids' : fields.one2many('cci_club.participation','group_id','Participers'),
        'session_ids' : fields.one2many('cci_club.session','group_id','Sessions'),
        'product_id' : fields.many2one('product.product','Associated product'),
        'host_id' : fields.many2one('res.partner','Host'),
        'hours' : fields.char('Hours',size=20),
        'day' : fields.selection([('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday')],'Day'),
        'agreement_nbr':fields.char('Agreement Nbr',size=16),
        'checks_type' : fields.selection([('none','Aucun'),('formation','Chèque-Formation'),('language','Chèque-Langue'),('both','Chèque-Formation et/ou langue')],'Checks'),
        'feder' : fields.boolean('Feder supported'),
        'liege' : fields.boolean('Liege'),
        'namur' : fields.boolean('Namur'),
        'session_count_by_invoice' : fields.integer('Number of sessions',help='Number of session by attendance to calculate the monthly revenue'),
        'checks_max' : fields.integer('Number of checks',help='Maximum number of checks for a participation in this club'),
        'level_id' : fields.many2one('cci_club.level','Average Level of Knowledge of this table'),
    }
    _defaults = {
        'waiting_club' : lambda *a: False,
        'feder' : lambda *a: False,
        'liege' : lambda *a: False,
        'namur' : lambda *a: False,
    }
club()

class language(osv.osv):
    _name = "cci_club.language"
    _description = "Language of the course for this participation"
    _columns = {
        'name' : fields.char('Name',size=32,required=True),
    }
language()

class participation_state(osv.osv):
    _name = "cci_club.participation_state"
    _description = "State of this participation"
    _columns = {
        'name' : fields.char('Name',size=64,required=True),
        'description' : fields.text('Description'),
        'current' : fields.boolean('Current',help="Indicate if a participation with this state must be considered as 'current' in the club"),
    }
participation_state()

class participation(osv.osv):
    _name = "cci_club.participation"
    _description = "Participation of a person in a club/group"
    _columns = {
        'group_id' : fields.many2one('cci_club.club','Club'),
        'partner_id' : fields.many2one('res.partner','Partner',required=True),
        'contact_id' : fields.many2one('res.partner.contact','Participer',required=True), 
        'date_registration' : fields.date('Registration date'),
        'date_to_invoice' : fields.date('Date to invoice'),
        'date_in' : fields.date('Beginning Date'),
        'date_out' : fields.date('End Date'),
        'language_id' : fields.many2one('cci_club.language','Language'),
        'level_id' : fields.many2one('cci_club.level','Level of Knowledge'),
        'availability' : fields.text('Availability'),
        'order_id' : fields.many2one('sale.order','Sale Order'),
        'provided_turnover' : fields.float('Provided turnover', digits=(16, 2)),
        'final_turnover' : fields.float('Final turnover', digits=(16, 2)),
        'salesman' : fields.many2one('res.users','Salesman'),
        'continuation' : fields.boolean('Continuation',help='Check if this participation is the followup of another one'),
        'state_id' : fields.many2one('cci_club.participation_state','State',required=True),
        'checksA' : fields.text('Checks Part 1'),
        'checksB' : fields.text('Checks Part 2'),
        'validChecksA' : fields.boolean('Valid checks Part 1',help='Check this if the first range of checks is in order'),
        'validChecksB' : fields.boolean('Valid checks Part 2',help='Check this if the second range of checks is in order'),
        'note' : fields.text('Internal note'),
        'attendance_ids' : fields.one2many('cci_club.attendance','participation_id','Attendances'),
        'membership' : fields.boolean('From membership',help='Indicate that this attendance came from a membership deal'),
    }
    _defaults = {
        'date_registration': lambda *a:time.strftime('%Y-%m-%d'),
    }
    def name_get(self,cr,uid,ids,context={}):
        if not len(ids):
            return []
        res = []
        for part in self.read(cr,uid,ids, ['contact_id','group_id'] ):
            res.append( (part['id'], "%s - %s" % (part['contact_id'][1], part['group_id'][1] ) ) )
        return res
participation()

class session_state(osv.osv):
    _name = "cci_club.session_state"
    _description = "The state of a session for managing the supplier invoices"
    _columns = {
        'name': fields.char('Name',size=50),
    }
session_state()

class session(osv.osv):
    _name = "cci_club.session"
    _description = "A session to a club"
    _columns = {
        'group_id': fields.many2one('cci_club.club','Club',required=True),
        'date': fields.date('Date',required=True),
        'number': fields.char('Number',size=20),
        'comments': fields.text('Comments'),
        'attendance_ids': fields.one2many('cci_club.attendance','session_id','Attendances'),
        'state_id': fields.many2one('cci_club.session_state','State'),
    }
    def name_get(self,cr,uid,ids,context={}):
        if not len(ids):
            return []
        res = []
        for session in self.read(cr,uid,ids, ['group_id','date'] ):
            res.append( (session['id'], "%s - %s" % (session['date'], session['group_id'][1] ) ) )
        return res
session()

class attendance_state(osv.osv):
    _name = "cci_club.attendance_state"
    _description = "State of attendance"
    _columns = {
        'name' : fields.char('Name',size=30),
        'checks_valid' : fields.boolean('Valid for Checks',help='Indicate that we can charge formative checks for this kind of attendance'),
    }
    _defaults = {
        'checks_valid' : lambda *a:True,
    }
attendance_state()

class attendance(osv.osv):
    _name = "cci_club.attendance"
    _description = "The attendance of a person in a club's session"
    _columns = {
        'participation_id' : fields.many2one('cci_club.participation','Participer',required=True),
        'session_id' : fields.many2one('cci_club.session','Session',required=True),
        'state' : fields.many2one('cci_club.attendance_state','State',required=True),
        'comments' : fields.text('Comments'),
    }
attendance()


