# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import fields,osv
from osv import orm
import netsvc
import pooler
import time
import tools
from tools.translate import _

class event_meeting_table(osv.osv):
    _name="event.meeting.table"
    _description="event.meeting.table"
    _columns={
        'partner_id1':fields.many2one('res.partner','First Partner',required=True),
        'partner_id2':fields.many2one('res.partner','Second Partner', required=True),
        'event_id':fields.many2one('event.event','Related Event', required=True),
        'contact_id1':fields.many2one('res.partner.contact','First Contact',required=True),
        'contact_id2':fields.many2one('res.partner.contact','Second Contact', required=True),
        'service':fields.integer('Service', required=True),
        'table':fields.char('Table',size=10,required=True),
        }
event_meeting_table()


class event_check_type(osv.osv):
    _name="event.check.type"
    _description="event.check.type"
    _columns={
        'name':fields.char('Name',size=20,required=True),
        }
event_check_type()

class event(osv.osv):

    def cci_event_fixed(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'fixed',})
        return True

    def cci_event_open(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'open',})
        return True

    def cci_event_confirm(self, cr, uid, ids, *args):
        for eve in self.browse(cr, uid, ids):
            if eve.mail_auto_confirm:
                #send reminder that will confirm the event for all the people that were already confirmed
                reg_ids = self.pool.get('event.registration').search(cr, uid, [('event_id','=',eve.id),('state','not in',['draft','cancel'])])
                if reg_ids:
                    self.pool.get('event.registration').mail_user_confirm(cr, uid, reg_ids)
        self.write(cr, uid, ids, {'state':'confirm',})

        return True

    def cci_event_running(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'running',})
        return True

    def cci_event_done(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'done',})
        return True

    def cci_event_closed(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'closed',})
        return True

    def cci_event_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancel',})
        reg_obj = self.pool.get('event.registration')
        reg_ids = reg_obj.search(cr, uid, [('event_id', 'in', ids)])
        reg_obj.cci_event_reg_cancel(cr, uid, reg_ids)
        return True

    def onchange_check_type(self, cr, uid, id, type):
        if not type:
            return {}
        tmp=self.pool.get('event.type').browse(cr, uid, type)
        return {'value':{'check_type' : tmp.check_type.id}}

    def _group_names(self, cr, uid, context=None):
        cr.execute('''
        SELECT distinct name
        FROM event_group
        ''')
        res = cr.fetchall()
        temp=[]
        for r in res:
            temp.append((r[0],r[0]))
        return temp

    _inherit="event.event"
    _description="event.event"
    _columns={
            'state': fields.selection([('draft','Draft'),('fixed','Fixed'),('open','Open'),('confirm','Confirmed'),('running','Running'),('done','Done'),('cancel','Canceled'),('closed','Closed')], 'State', readonly=True, required=True),
            'agreement_nbr':fields.char('Agreement Nbr',size=16),
            'note':fields.text('Note'),
            'fse_code':fields.char('FSE code',size=64),
            'fse_hours':fields.integer('FSE Hours'),
            'signet_type':fields.selection(_group_names, 'Signet type'),
            'localisation':fields.char('Localisation',size=20),
            'check_type': fields.many2one('event.check.type','Check Type'),
            'name_on_site': fields.char('Name on Site',size=128),
            }
event()

class event_check(osv.osv):
    _name="event.check"
    _description="event.check"

    def cci_event_check_block(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'block',})
        return True

    def cci_event_check_confirm(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'confirm',})
        return True

    def cci_event_check_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancel',})
        return True

    _columns={
        "name": fields.char('Name', size=128, required=True),
        "code": fields.char('Code', size=64),
        "reg_id": fields.many2one('event.registration','Inscriptions',required=True),
        "state": fields.selection([('draft','Draft'),('block','Blocked'),('confirm','Confirm'),('cancel','Cancel'),('asked','Asked')], 'State', readonly=True),
        "unit_nbr": fields.float('Value'),
        "type_id":fields.many2one('event.check.type','Type'),
        "date_reception":fields.date("Reception Date"),
        "date_limit":fields.date('Limit Date'),
        "date_submission":fields.date("Submission Date"),
        }
    _defaults = {
        'state': lambda *args: 'draft',
        'name': lambda *args: 'cheque',
    }

event_check()

class event_type(osv.osv):
    _inherit = 'event.type'
    _description= 'Event type'
    _columns = {
        'check_type': fields.many2one('event.check.type','Default Check Type'),
    }
event_type()

class event_group(osv.osv):
    _name= 'event.group'
    _description = 'event.group'
    _columns = {
        "name":fields.char('Group Name',size=20,required=True),
        "bookmark_name":fields.char('Value',size=128),
        "picture":fields.binary('Picture'),
        "type":fields.selection([('image','Image'),('text','Text')], 'Type',required=True)
        }
    _defaults = {
        'type': lambda *args: 'text',
    }

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        result = []
        for line in self.browse(cr, uid, ids, context):
            if line.bookmark_name:
                result.append((line.id, (line.name + ' - ' + line.bookmark_name)))
            else:
                result.append((line.id, line.name))
        return result

event_group()

class event_registration(osv.osv):

    def create(self, cr, uid, vals, *args, **kwargs):
#       Overwrite the name fields to set next sequence according to the sequence in the legalization type (type_id)
        if vals['name'] == 'Registration:' or vals['name'] == 'Registration':
            vals['name'] = False # to be sure to have the contact name with 'Registration'
        print "inside 1"
        print vals
        vals['badge_name'] = vals['badge_title'] = vals['badge_partner'] = False
        if not vals['badge_name'] or not vals['name']:
            newvals = self.onchange_contact_id(cr, uid, [], vals['contact_id'], vals['partner_id'] )
            if newvals['value'].has_key('badge_name'):
                vals.update({'badge_name':newvals['value']['badge_name']})
            if newvals['value'].has_key('badge_title'):
                vals.update({'badge_title':newvals['value']['badge_title']})
            if newvals['value'].has_key('name'):
                vals.update({'name':newvals['value']['name']})
            if newvals['value'].has_key('email_from'):
                vals.update({'email_from':newvals['value']['email_from']})
        if not vals['badge_partner']:
            newvals =  self.onchange_partner_id(cr, uid, [], vals['partner_id'], vals['event_id'], False)
            if newvals['value'].has_key('badge_partner'):
                vals.update({'badge_partner':newvals['value']['badge_partner']})
            # maybe unit_price and partner_invoice_id
        return super(event_registration,self).create(cr, uid, vals, *args, **kwargs)

    def cci_event_reg_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft',})
        self.pool.get('event.registration')._history(cr, uid, ids, 'Draft', history=True)
        return True

    def cci_event_reg_open(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'open',})
        for registration in self.browse(cr, uid, ids, {}):
            if registration.event_id.mail_auto_confirm or registration.event_id.mail_auto_registr:
                self.pool.get('event.registration').mail_user(cr,uid,ids)
        self.pool.get('event.registration')._history(cr, uid, ids, 'Open', history=True)
        return True

    def cci_event_reg_done(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'done',})
        self.pool.get('event.registration')._history(cr, uid, ids, 'Done', history=True)
        return True

    def cci_event_reg_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancel','unit_price':0.0})
        self.pool.get('event.registration')._history(cr, uid, ids, 'Cancel', history=True)
        return True

    def cal_check_amount(self, cr, uid, ids, name, arg, context={}):
        res = {}
        data_reg = self.browse(cr,uid,ids)
        for reg in data_reg:
            total = 0
            for check in reg.check_ids:
                total = total + check.unit_nbr
            res[reg.id] = total
        return res

    def get_nbr_checks(self, cr, uid, ids, name, arg, context={}):
        res = {}
        data_reg = self.browse(cr, uid, ids, context=context)
        for reg in data_reg:
            res[reg.id] = len(reg.check_ids)
        return res

    def _create_invoice_lines(self, cr, uid, ids, vals):
        for reg in self.browse(cr, uid, ids):
            note = ''
            cci_special_reference = False
            if reg.check_mode:
                note = 'Check payment for a total of ' + str(reg.check_amount)
                cci_special_reference = "event.registration*" + str(reg.id)
                vals.update({
                    'note': note,
                    'cci_special_reference': cci_special_reference,
                })
        return self.pool.get('account.invoice.line').create(cr, uid,vals)

    # this method overwrites the parent method to make it more adapted to CCI events
    def mail_user_confirm(self,cr,uid,ids):
        reg_ids=self.browse(cr,uid,ids)
        for reg_id in reg_ids:
            src = reg_id.event_id.reply_to or False
            #if not reg_id.email_from:
            #    raise osv.except_osv(_('Warning!'), _('You should specify Partner Email for registration "%s" !')%(reg_id.name,))
            dest = []
            if reg_id.email_from:
                dest += [reg_id.email_from]
                if reg_id.email_cc:
                    dest += [reg_id.email_cc]
            if dest and src:
                tools.email_send(src, dest,'Infos pratiques et liste des participants '+( reg_id.event_id.name_on_site and reg_id.event_id.name_on_site or reg_id.event_id.product_id.name ), reg_id.event_id.mail_confirm, tinycrm = str(reg_id.case_id.id),subtype='html')

            if not src:
                raise osv.except_osv(_('Error!'), _('You must define a reply-to address in order to mail the participant. You can do this in the Mailing tab of your event. Note that this is also the place where you can configure your event to not send emails automaticly while registering'))
        return False

    # this method overwrites the parent method to make it more adapted to CCI events
    def mail_user(self,cr,uid,ids):
        reg_ids=self.browse(cr,uid,ids)
        for reg_id in reg_ids:
            flag = ''
            src = reg_id.event_id.reply_to or False
            dest = []
            if reg_id.email_from:
                dest += [reg_id.email_from]
                if reg_id.email_cc:
                    dest += [reg_id.email_cc]
            if reg_id.event_id.mail_auto_confirm or reg_id.event_id.mail_auto_registr:
                #if not reg_id.email_from:
                #    raise osv.except_osv(_('Warning!'), _('You should specify Partner Email for registration "%s" !')%(reg_id.name,))
                if dest and src:
                    if (reg_id.event_id.state in ['confirm','running']) and reg_id.event_id.mail_auto_confirm :
                        flag = 't'
                        tools.email_send(src, dest,'Infos pratiques et liste des participants '+( reg_id.event_id.name_on_site and reg_id.event_id.name_on_site or reg_id.event_id.product_id.name ), reg_id.event_id.mail_confirm, tinycrm = str(reg_id.case_id.id),subtype='html')
                    if reg_id.event_id.state in ['draft', 'fixed', 'open','confirm','running'] and reg_id.event_id.mail_auto_registr and not flag:
                        tools.email_send(src, dest,'Confirmation inscription '+( reg_id.event_id.name_on_site and reg_id.event_id.name_on_site or reg_id.event_id.product_id.name), reg_id.event_id.mail_registr, tinycrm = str(reg_id.case_id.id),subtype='html')
                if not src:
                    raise osv.except_osv(_('Error!'), _('You must define a reply-to address in order to mail the participant. You can do this in the Mailing tab of your event. Note that this is also the place where you can configure your event to not send emails automaticly while registering'))
        return False

    _inherit = 'event.registration'
    _description="event.registration"
    _columns={
            "contact_order_id":fields.many2one('res.partner.contact','Contact Order'),
            "grp_id": fields.many2one('event.group','Event Group'),
            "cavalier": fields.boolean('Cavalier',help="Check if we should print papers with participant name"),
            "payment_mode":fields.many2one('payment.mode',"Payment Mode"),
            "payment_linked":fields.many2one('account.move.line',"Linked Payment", domain=[('reconcile_id','=',False),('reconcile_partial_id','=',False)]),
            "check_mode":fields.boolean('Check Mode'),
            "check_ids":fields.one2many('event.check','reg_id',"Check ids"),
            "payment_ids":fields.many2many("account.move.line","move_line_registration", "reg_id", "move_line_id","Payment", readonly=True),
            "training_authorization":fields.char('Training Auth.',size=12,help='Formation Checks Authorization number',readonly=True),
            "check_amount":fields.function(cal_check_amount,method=True,type='float', string='Check Amount'),
            "nbr_event_check": fields.function(get_nbr_checks, method=True, type='integer', string="Number of Checks", help="This field simply computes the number of event check records for this registration"),
            "comments": fields.text('Comments'),
            "ask_attest": fields.boolean('Ask an attestation'),
    }
    _defaults = {
        'name': lambda *a: 'Registration',
    }

#    def onchange_contact_id(self, cr, uid, ids, contact, partner):
#        data = super(event_registration,self).onchange_contact_id(cr, uid, ids, contact, partner)
#        if not contact:
#            return data
#        contact = self.pool.get('res.partner.contact').browse(cr, uid, contact)
#        if contact.badge_name:
#            data['value']['badge_name'] = contact.badge_name
#        if contact.badge_title:
#            data['value']['badge_title'] = contact.badge_title
#        return data
    # overwrites complety the parent (event) method to accomodate to CCI way of life
    def onchange_contact_id(self, cr, uid, ids, contact, partner):
        data ={}
        if not contact:
            return data
        contact_id = self.pool.get('res.partner.contact').browse(cr, uid, contact)
        data['badge_name'] = contact_id.badge_name and contact_id.badge_name or ( contact_id.name + ' ' + contact_id.first_name ).strip()
        if partner:
            partner_addresses = self.pool.get('res.partner.address').search(cr, uid, [('partner_id','=',partner)])
            job_ids = self.pool.get('res.partner.job').search(cr, uid, [('contact_id','=',contact),('address_id','in',partner_addresses)])
            if job_ids:
                data['email_from'] = self.pool.get('res.partner.job').browse(cr, uid, job_ids[0]).email
                data['badge_title'] = contact_id.badge_title and contact_id.badge_title or self.pool.get('res.partner.job').browse(cr, uid, job_ids[0]).function_label
        d = self.onchange_badge_name(cr, uid, ids,data['badge_name'])
        data.update(d['value'])

        return {'value':data}

    def onchange_partner_id(self, cr, uid, ids, part, event_id, email=False):
        #raise an error if the partner cannot participate to event.
        badge_part = False
        warning = False
        if part:
            data_partner = self.pool.get('res.partner').browse(cr,uid,part)
            if data_partner.alert_events:
                warning = {
                    'title': "Warning:",
                    'message': data_partner.alert_explanation or 'Partner is not valid'
                        }
            if data_partner.badge_partner:
                badge_part = data_partner.badge_partner
        data = super(event_registration,self).onchange_partner_id(cr, uid, ids, part, event_id, email)
        if badge_part:
            data['value']['badge_partner'] = badge_part
        if warning:
            data['warning'] =  warning
        return data

    def onchange_partner_invoice_id(self, cr, uid, ids, event_id, partner_invoice_id):
        data={}
        context={}
        data['training_authorization']=data['unit_price']=False
        if partner_invoice_id:
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_invoice_id)
            data['training_authorization']=data_partner.training_authorization
        if not event_id:
            return {'value':data}
        data_event =  self.pool.get('event.event').browse(cr,uid,event_id)

        if data_event.product_id:
            if not partner_invoice_id:
                data['training_authorization']=False
                data['unit_price']=self.pool.get('product.product').price_get(cr, uid, [data_event.product_id.id],context=context)[data_event.product_id.id]
                return {'value':data}
            data_partner = self.pool.get('res.partner').browse(cr,uid,partner_invoice_id)
            context.update({'partner_id':data_partner and data_partner.id})
            data['unit_price']=self.pool.get('product.product').price_get(cr, uid, [data_event.product_id.id],context=context)[data_event.product_id.id]
            return {'value':data}
        return {'value':data}

event_registration()


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns={
        "case_id" : fields.many2many("event.registration","move_line_registration", "move_line_id", "reg_id","Registration"),
    }
account_move_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

