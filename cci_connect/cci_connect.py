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
import datetime
from osv import fields, osv

def _partner_title_get(self, cr, uid, context={}):
    obj = self.pool.get('res.partner.title')
    ids = obj.search(cr, uid, [('domain', '=', 'partner')])
    res = obj.read(cr, uid, ids, ['shortcut','name'], context)
    return [(r['shortcut'], r['name']) for r in res] +  [('','')]

class delayed_partner(osv.osv):
    _name = "cci_connect.delayed_partner"
    _description = "store asked changes for partner and address from internet site"
    _columns = {
        'partner_id' : fields.many2one('res.partner','Partner',required=True),
        'address_id' : fields.many2one('res.partner.address','Address',required=True),
        'partner_name' : fields.char('Name', size=128 ),
        'partner_title' : fields.char('Title', size=16, translate=True),
        'website': fields.char('Website',size=64),
        'vat': fields.char('VAT',size=32),
        'searching' : fields.text('Searching'),
        'selling' : fields.text('Selling'),
        'address_name': fields.char('Address Name', size=64),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip_id':fields.many2one('res.partner.zip','Zip'),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('Site E-Mail', size=240),
        'phone': fields.char('Site Phone', size=64),
        'fax': fields.char('Site Fax', size=64),
        'activity': fields.text('Activity'),
        'old_functions': fields.char('Old functions', size=255),
        'asker_id' : fields.many2one('res.partner.contact','Asker for Change'),
        'state': fields.selection([('draft','Draft'),('done','Done'),('cancel','Canceled')],'State'),
        'state_changed': fields.date('Status Changed'),
        'final_partner_name' : fields.char('Final Partner Name', size=128 ),
        #'final_partner_title' : fields.char('Final Title', size=16),
        'final_partner_title' : fields.selection(_partner_title_get, 'Title', size=32),
        #'final_partner_title' : fields.many2one('res.partner.title','Final Title',domain="[('domain','=','partner')]"),
        'final_website': fields.char('Final Website',size=64),
        'final_vat': fields.char('Final VAT',size=32),
        'final_searching' : fields.text('Final Searching'),
        'final_selling' : fields.text('Final Selling'),
        'final_address_name': fields.char('Final Address Name', size=64),
        'final_street': fields.char('Final Street', size=128),
        'final_street2': fields.char('Final Street2', size=128),
        'final_zip_id':fields.many2one('res.partner.zip','Final Zip'),
        'final_country_id': fields.many2one('res.country', 'Final Country'),
        'final_email': fields.char('Final Site E-Mail', size=240),
        'final_phone': fields.char('Final Site Phone', size=64),
        'final_fax': fields.char('Final Site Fax', size=64),
        'final_activity': fields.text('Final activity'),
        'current_partner_name': fields.related('partner_id','name',type="char",size="128",string="Current Partner Name", store=False),
        'current_partner_title': fields.related('partner_id','title',type="char",size="30",string="Current Partner Title", store=False),
        'current_website': fields.related('partner_id','website',type="char",size="120",string="Current Partner WebSite", store=False),
        'current_vat':fields.related('partner_id','vat',type="char",size="30",string="Current Partner VAT", store=False),
        'current_address_name': fields.related('address_id','name',type="char",size="128",string="Current Partner VAT", store=False),
        'current_street': fields.related('address_id','street',type="char",size="128",string="Current Partner VAT", store=False),
        'current_street2': fields.related('address_id','street2',type="char",size="128",string="Current Partner VAT", store=False),
        'current_zip_id': fields.related('address_id','zip_id',type="many2one",relation="res.partner.zip",string="Current Address Zip Code", store=False),
        'current_country_id': fields.related('address_id','country_id',type="many2one",relation="res.country",string="Current Address Country", store=False),
        'current_email': fields.related('address_id','email',type="char",size="128",string="Current Site EMail", store=False),
        'current_phone': fields.related('address_id','phone',type="char",size="60",string="Current Site Phone", store=False),
        'current_fax': fields.related('address_id','fax',type="char",size="60",string="Current Site Fax", store=False),
        'current_activity': fields.related('partner_id','activity_description',type='text',string='Current Activity', store=False),
    }
    def but_cancel(self,cr,uid,ids,*args,**kw):
        self.write(cr, uid, ids, {'state':'cancel','state_changed':datetime.date.today().strftime('%Y-%m-%d')})
        return True
    def but_confirm_changes(self,cr,uid,ids,*args,**kw):
        self.write(cr, uid, ids, {'state':'done','state_changed':datetime.date.today().strftime('%Y-%m-%d')})
        for delay in self.browse(cr, uid, ids):
            if delay.final_partner_name or delay.final_partner_title or delay.final_website or delay.final_vat or delay.final_activity:
                obj_partner = self.pool.get('res.partner')
                changes = {}
                if delay.final_partner_name:
                    changes['name'] = delay.final_partner_name
                if delay.final_partner_title:
                    changes['title'] = delay.final_partner_title
                if delay.final_website:
                    changes['website'] = delay.final_website
                if delay.final_vat:
                    changes['vat'] = delay.final_vat
                if delay.final_activity:
                    changes['activity_description'] = delay.final_activity
                obj_partner.write(cr, uid, [delay.partner_id.id], changes, {'lang':'fr_FR'} )
            if delay.final_address_name or delay.final_street or delay.final_street2 or delay.final_zip_id \
                or delay.final_country_id or delay.final_email or delay.final_phone or delay.final_fax:
                obj_addr = self.pool.get('res.partner.address')
                changes = {}
                if delay.final_address_name:
                    changes['name'] = delay.final_address_name
                if delay.final_street:
                    changes['street'] = delay.final_street
                if delay.final_street2:
                    changes['street2'] = delay.final_street2
                if delay.final_email:
                    changes['email'] = delay.final_email
                if delay.final_phone:
                    changes['phone'] = delay.final_phone
                if delay.final_fax:
                    changes['fax'] = delay.final_fax
                obj_addr.write(cr, uid, [delay.address_id.id], changes )
            if delay.final_searching:
                obj_partner = self.pool.get('res.partner')
                query = """
                    select a.id from partner_question_rel as rel, crm_profiling_answer as a
                    where a.question_id = 101 and rel.answer = a.id and rel.partner =%d limit 1"""% delay.partner_id.id
                cr.execute(query)
                answer_id = cr.fetchone()
                if answer_id:
                    answer_id = answer_id[0]
                    obj_answer = self.pool.get('crm_profiling.answer')
                    obj_answer.write(cr, uid, [answer_id], {'name':'/','text':delay.final_searching})
                else:
                    obj_answer = self.pool.get('crm_profiling.answer')
                    new_id = obj_answer.create(cr, uid, {'question_id':101,'name':'/','text':delay.final_searching})
                    query = """
                        select distinct(answer) from partner_question_rel
                        where partner =%d"""% delay.partner_id.id
                    cr.execute(query)
                    temp = []
                    for x in cr.fetchall():
                        temp.append(x[0])
                    temp.append(new_id)
                    obj_partner.write(cr, uid, [delay.partner_id.id],{'answers_ids':[[6,0,temp]]})
            if delay.final_selling:
                obj_partner = self.pool.get('res.partner')
                query = """
                    select a.id from partner_question_rel as rel, crm_profiling_answer as a
                    where a.question_id = 102 and rel.answer = a.id and rel.partner =%d limit 1"""% delay.partner_id.id
                cr.execute(query)
                answer_id = cr.fetchone()
                if answer_id:
                    answer_id = answer_id[0]
                    obj_answer = self.pool.get('crm_profiling.answer')
                    obj_answer.write(cr, uid, [answer_id], {'name':'/','text':delay.final_selling})
                else:
                    obj_answer = self.pool.get('crm_profiling.answer')
                    new_id = obj_answer.create(cr, uid, {'question_id':102,'name':'/','text':delay.final_selling})
                    query = """
                        select distinct(answer) from partner_question_rel
                        where partner =%d"""% delay.partner_id.id
                    cr.execute(query)
                    temp = []
                    for x in cr.fetchall():
                        temp.append(x[0])
                    temp.append(new_id)
                    obj_partner.write(cr, uid, [delay.partner_id.id],{'answers_ids':[[6,0,temp]]})
        return True
delayed_partner()

