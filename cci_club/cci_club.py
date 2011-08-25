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
# Version 1.1 : Philmer 2011-07-03
#                added the management of unlink to clubs and participations,
#                and copy in clubs
#               Philmer 2011-08-16
#                added the management of attendances in copy and 
#                unlink of participations
import time
import datetime
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
    def _get_active_participations(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for club in self.browse(cr,uid,ids):
            count = 0
            total_provided_turnover = total_final_turnover = 0.0
            if club.participation_ids:
                for participation in club.participation_ids:
                    if participation.state_id.current and ( not participation.date_out or participation.date_out >= datetime.date.today().strftime('%Y-%m-%d') ):
                        count += 1
                        total_provided_turnover += participation.provided_turnover
                        total_final_turnover += participation.final_turnover
            res[club.id] = "Ce club totalise %s participants actifs pour un C.A. prévu-réel de %.2f-%.2f" % (str(count),total_provided_turnover,total_final_turnover)
        return res
    def _count_active_participations(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for club in self.browse(cr,uid,ids):
            count = 0
            if club.participation_ids:
                for participation in club.participation_ids:
                    if participation.state_id.current and ( not participation.date_out or participation.date_out >= datetime.date.today().strftime('%Y-%m-%d') ):
                        count += 1
            res[club.id] = count
        return res
    def write(self, cr, uid, ids,vals,context=None):
        self._get_active_participations(cr, uid, ids, None, None, context)
        return super(osv.osv,self).write(cr, uid, ids,vals, context)
    def copy(self, cr, uid, id, default=None, context={}):
        part = self.read(cr,uid,id,['name','code'])
        if not default:
            default = {}
        default.update({
            'name':part['name']+' (copy)',
            'code':part['code']+' (copy)',
            'participation_ids': False,
            'session_ids':False,
        })
        return super(club, self).copy(cr, uid, id, default, context)
    def unlink(self,cr,uid,ids,context):
        empty = True
        for club in self.browse(cr,uid,ids):
            if len(club.participation_ids) > 0:
                empty = False
        if empty:
            return super(osv.osv,self).unlink(cr,uid,ids,context)
        else:
            raise osv.except_osv('Error!',"You can't delete a club with participations !")
            return False

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
        'department_id' : fields.many2one('hr.department','Department'),
        #'selected_participation_ids' : fields.one2many('cci_club.participation','group_id','Participers',domain=[('current','=',True)]),
        'selected_participation_count' : fields.function(
            _count_active_participations,
            type='integer',
            method=True,
            string='Active Participers'),
        'count_active' : fields.function(
            _get_active_participations,
            type='char',
            size=90,
            method=True,
            string='Active Participations'),
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
        #'color': fields.selection([('black','Black'),('red','Red'),('blue','Blue'),('green','Green'),('darkred','Dark Red'),('darkblue','Dark Blue'),('darkgreen','Dark Green'),('grey','Grey'),('yellow','Yellow'),('pink','Pink')], 'Color',help="Color of the line in the list of participation"),
    }
    #_defaults = {
    #    'color': lambda *a:'black',
    #}
participation_state()

class participation(osv.osv):
    def _get_default_phone(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            if rec.contact_id and rec.contact_id.job_id and rec.contact_id.job_id.phone:
                result[rec.id] = rec.contact_id.job_id.phone + ' (Job)'
            elif rec.contact_id and rec.contact_id.mobile:
                result[rec.id] = rec.contact_id.mobile + ' (Mobile contact)'
            elif rec.contact_id and rec.contact_id.job_id and rec.contact_id.job_id.address_id and rec.contact_id.job_id.address_id.phone:
                result[rec.id] = rec.contact_id.job_id.address_id.phone + ' (Address)'
            else:
                result[rec.id] = ''
        return result

    def _get_default_email(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            if rec.contact_id and rec.contact_id.job_id and rec.contact_id.job_id.email:
                result[rec.id] = rec.contact_id.job_id.email
            elif rec.contact_id and rec.contact_id.email:
                result[rec.id] = rec.contact_id.email
            elif rec.contact_id and rec.contact_id.job_id and rec.contact_id.job_id.address_id and rec.contact_id.job_id.address_id.email:
                result[rec.id] = rec.contact_id.job_id.address_id.email
            else:
                result[rec.id] = ''
        return result

    def _get_locality(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            if rec.contact_id and rec.contact_id.job_id and rec.contact_id.job_id.address_id and rec.contact_id.job_id.address_id.partner_id and rec.contact_id.job_id.address_id.partner_id == rec.partner_id:
                result[rec.id] = rec.contact_id.job_id.address_id.zip_id.name + ' ' + rec.contact_id.job_id.address_id.zip_id.city
            else:
                result[rec.id] = ''
        return result

    def _get_current_date(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        today = datetime
        for id in ids:
             result[id] = datetime.datetime.today().strftime('%Y-%m-%d')
        return result

    def _get_invoice_data(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = ''
            if rec.order_id and rec.order_id.invoice_ids:
                for invoice in rec.order_id.invoice_ids:
                    if invoice.number:
                        if result[rec.id]:
                            result[rec.id] += "; "
                        result[rec.id] += ( "%s (%s)" % (invoice.number,invoice.date_invoice[8:10]+'/'+invoice.date_invoice[5:7]+'/'+invoice.date_invoice[0:4]) )
        return result

    def onchange_contact(self, cr, uid, ids, contact_id, partner_id):
        if contact_id:
            # get the email address
            contact = self.pool.get('res.partner.contact').browse(cr, uid, contact_id)
            if contact.job_id and contact.job_id.email:
                newvalues = {'email':contact.job_id.email}
            elif contact.email:
                newvalues = {'email':contact.email}
            elif contact.job_id and contact.job_id.address_id and contact.job_id.address_id.email:
                newvalues = {'email':contact.job_id.address_id.email}
            else:
                newvalues = {'email':''}
            # get the phone
            if contact.job_id and contact.job_id.phone:
                newvalues['phone'] = contact.job_id.phone + ' (Job)'
            elif contact.mobile:
                newvalues['phone'] = contact.mobile + ' (Mobile contact)'
            elif contact.job_id and contact.job_id.address_id and contact.job_id.address_id.phone:
                newvalues['phone'] = contact.job_id.address_id.phone + ' (Address)'
            else:
                newvalues['phone'] = ''
        elif partner_id:
            newvalues = {'email':'','phone':''}
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner.address:
                for add in partner.address:
                    if add.type == 'default':
                        if add.email:
                            newvalues['email'] = add.email
                        if add.phone:
                            newvalues['phone'] = add.phone + ' (Address)'
                        break
        else:
            newvalues = {'email':'','phone':''}
        return {'value':newvalues}

    def name_get(self,cr,uid,ids,context={}):
        if not len(ids):
            return []
        res = []
        for part in self.read(cr,uid,ids, ['contact_id','group_id'] ):
            res.append( (part['id'], "%s - %s" % (part['contact_id'][1], part['group_id'][1] ) ) )
        return res

    def onchange_partner(self, cr, uid, ids, partner_id, group_id, contact_id):
        warning = False
        if partner_id:
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            if data_partner.alert_others:
                warning = {
                    'title': "Warning:",
                    'message': data_partner.alert_explanation or 'Partner is not valid'
                        }
        newvalues={'salesman':False,'provided_turnover':False,'email':'','phone':''}
        context={}
        if partner_id:
            newvalues['salesman']=data_partner.user_id.id

            if group_id:
                data_club = self.pool.get('cci_club.club').browse(cr,uid,group_id)
                if data_club['product_id']:
                    context.update({'partner_id':data_partner and data_partner.id})
                    newvalues['provided_turnover']=self.pool.get('product.product').price_get(cr, uid, [data_club.product_id.id],context=context)[data_club.product_id.id]

        if contact_id:
            # get the email address
            contact = self.pool.get('res.partner.contact').browse(cr, uid, contact_id)
            if contact.job_id and contact.job_id.email:
                newvalues = {'email':contact.job_id.email}
            elif contact.email:
                newvalues = {'email':contact.email}
            elif contact.job_id and contact.job_id.address_id and contact.job_id.address_id.email:
                newvalues = {'email':contact.job_id.address_id.email}
            else:
                newvalues = {'email':''}
            # get the phone
            if contact.job_id and contact.job_id.phone:
                newvalues['phone'] = contact.job_id.phone + ' (Job)'
            elif contact.mobile:
                newvalues['phone'] = contact.mobile + ' (Mobile contact)'
            elif contact.job_id and contact.job_id.address_id and contact.job_id.address_id.phone:
                newvalues['phone'] = contact.job_id.address_id.phone + ' (Address)'
            else:
                newvalues['phone'] = ''
        elif partner_id:
            if data_partner.address:
                for add in data_partner.address:
                    if add.type == 'default':
                        if add.email:
                            newvalues['email'] = add.email
                        if add.phone:
                            newvalues['phone'] = add.phone + ' (Address)'
                        break
        return {'value':newvalues}

    def onchange_group_id(self, cr, uid, ids, group_id, partner_id):
        data={}
        context={}
        data['provided_turnover']=False
        if partner_id and group_id:
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            data_club = self.pool.get('cci_club.club').browse(cr,uid,group_id)
            if data_club['product_id']:
                context.update({'partner_id':data_partner and data_partner.id})
                data['provided_turnover']=self.pool.get('product.product').price_get(cr, uid, [data_club.product_id.id],context=context)[data_club.product_id.id]
        return {'value':data}

    def copy(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        default.update({
            'order_id': False,
            'attendance_ids': False,
        })
        return super(participation, self).copy(cr, uid, id, default, context)
    def unlink(self,cr,uid,ids,context):
        logs = self.pool.get('cci_club.participation_log')
        for part in self.browse(cr,uid,ids):
            log_ids = logs.search(cr,uid,[('participation_id','=',part.id)])
            logs.unlink(cr,uid,log_ids)
        attendances = self.pool.get('cci_club.attendance')
        for part in self.browse(cr,uid,ids):
            att_ids = attendances.search(cr,uid,[('participation_id','=',part.id)])
            attendances.unlink(cr,uid,att_ids)
        return super(osv.osv,self).unlink(cr, uid, ids,context)

    def search(self, cr, user, targs, offset=0, limit=None, order=None, context=None, count=False):
        part_ids = []
        for targ in targs:
            if targ[0] == 'contact_id' and targ[1] == 'ilike':
                contact_obj = self.pool.get('res.partner.contact')
                search_arg = ['|', ('first_name', 'ilike', targ[2]), ('name', 'ilike', targ[2])]
                contact_ids = contact_obj.search(cr, user, search_arg, offset=offset, limit=None, order=order, context=context, count=count)
                if not contact_ids:
                    if targ[2].count(' ') == 1:
                        (ename,efirst) = targ[2].split(' ')
                        search_arg = [('first_name','ilike',efirst),('name','ilike',ename)]
                        contact_ids = contact_obj.search(cr, user, search_arg, offset=offset, limit=None, order=order, context=context, count=count)
                        if not contact_ids:
                            # no results to first search and not exactly one space separator => nothing to find
                            continue
                    else:
                        # no results to first search and not exactly one space separator => nothing to find
                        continue
                contacts = contact_obj.browse(cr, user, contact_ids, context=context)
                for contact in contacts:
                    part_ids.extend([item.id for item in contact.club_participation_ids])
        res = super(participation,self).search(cr, user, targs, offset=offset, limit=limit, order=order, context=context, count=count)
        if part_ids:
                res = list(set(res + part_ids))
        return res
    def write(self, cr, uid, ids,vals,context=None):
        if len(ids) == 1 and vals.has_key('state_id'): # NOT POSSIBLE TO HAVE A WRITE ON STATE_ID FROM A TREE
            old_value = self.pool.get('cci_club.participation').read(cr,uid,ids,['state_id'])[0]
            if old_value['state_id'][0] != vals['state_id']:
                log_values = {'participation_id':ids[0], 'old_state_id':old_value['state_id'][0], 'new_state_id':vals['state_id'], 'user_id':uid, 'datetime': datetime.datetime.now()}
                log_obj = self.pool.get('cci_club.participation_log')
                result = log_obj.create(cr,uid,log_values)
        return super(osv.osv,self).write(cr, uid, ids,vals, context)

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
        'checks_a' : fields.text('Checks Part 1'),
        'checks_b' : fields.text('Checks Part 2'),
        'valid_checks_a' : fields.boolean('Valid checks Part 1',help='Check this if the first range of checks is in order'),
        'valid_checks_b' : fields.boolean('Valid checks Part 2',help='Check this if the second range of checks is in order'),
        'note' : fields.text('Internal note'),
        'attendance_ids' : fields.one2many('cci_club.attendance','participation_id','Attendances'),
        'membership' : fields.boolean('From membership',help='Indicate that this attendance came from a membership deal'),
        'phone': fields.function(_get_default_phone, method=True, string='Phone', type='char',size=60),
        'email': fields.function(_get_default_email, method=True, string='Email', type='char',size=240),
        'zip_loc' : fields.function(_get_locality,method=True, string='Zip and City', type='char', size='80'),
        'invoice_data' : fields.function(_get_invoice_data,method=True, string='Invoice data', type='char', size='80'),
        'current_date' : fields.function(_get_current_date,method=True, type='char', size='10', string='Today'),
    }
    _defaults = {
        'date_registration': lambda *a:time.strftime('%Y-%m-%d'),
    }
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

class participation_log(osv.osv):
    _name = "cci_club.participation_log"
    _description = "Log of all states changes"
    _columns = {
        'participation_id' : fields.many2one('cci_club.participation','Participer',required=True),
        'old_state_id' : fields.many2one('cci_club.participation_state','Old State'),
        'new_state_id' : fields.many2one('cci_club.participation_state','New State'),
        'user_id' : fields.many2one('res.users','Change Responsible'),
        'datetime' : fields.datetime('Change DateTime'),
    }
    _defaults = {
        'datetime' : lambda *a: datetime.datetime.now(),
    }
participation_log()

class res_partner_contact(osv.osv):
    _inherit = "res.partner.contact"
    _columns = {
        'club_participation_ids': fields.one2many('cci_club.participation','contact_id','Participations to clubs'),
    }
res_partner_contact()
