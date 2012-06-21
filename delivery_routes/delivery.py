# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Cubic ERP - Teradata SAC. (http://cubicerp.com).
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

from osv import fields, osv
import time
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class delivery_driver(osv.osv):
    _name='delivery.driver'
    _columns = {
            'partner_id': fields.many2one('res.partner','Partner',help='Fill this field if the driver is a outsourcing of the company'),
            'employee_id': fields.many2one('hr.employee','Employee',help='Fill this if the driver is a employee of the company'),
            'name': fields.char('Name', size=64, required=True),
            'carrier_id': fields.many2one('delivery.carrier','Carrier'),
            'outsourcing': fields.boolean('Outsourcing'),
            'route_ids': fields.one2many('delivery.route','driver_id','Delivery Routes'),
        }
    _defaults = {
            'outsourcing': False,
        }

delivery_driver()


class delivery_time(osv.osv):
    _name='delivery.time'
    _columns = {
            'sequence': fields.integer('Sequence'),
            'name': fields.char('Name', size=64, required=True),
            'start_hour': fields.selection(([(str(x),str(x)) for x in range(0,24)] + [('-','--')]),'Start Hour'),
            'start_minute': fields.selection(([(str(x*5),str(x*5)) for x in range(0,12)] + [('-','--')]),'Start Minute'),
            'end_hour': fields.selection(([(str(x),str(x)) for x in range(0,24)] + [('-','--')]),'End Hour'),
            'end_minute': fields.selection(([(str(x*5),str(x*5)) for x in range(0,12)] + [('-','--')]),'End Minute'),
            'active': fields.boolean('Active'),
        }
    _defaults = {
            'active': True,
        }

delivery_time()


class delivery_carrier(osv.osv):
    _name = "delivery.carrier"
    _inherit = "delivery.carrier"

    _columns = {
            'driver_ids' : fields.one2many('delivery.driver','carrier_id','Delivery Drivers'),
        }

delivery_carrier()

#TODO: Add vehicle class (usually from maintenance module)
class delivery_route(osv.osv):
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'delivery.route'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(delivery_route, self).create(cr, user, vals, context)
        return new_id
    
    _name='delivery.route'
    _columns = {
            'name': fields.char('Reference', size=64, required=True, select=True),
            'date': fields.date('Date', required=True, select=True),
            'time_id': fields.many2one('delivery.time','Delivery Time', select=True),
            'driver_id': fields.many2one('delivery.driver','Delivery Driver', required=True),
            'state': fields.selection([
                                ('draft','Draft'),
                                ('departure','Departure'),
                                ('arrive','Arrive'),
                                ('done', 'Done'),
                                ('cancel','Cancel')],'State',readonly=True),
            'line_ids': fields.one2many('delivery.route.line','route_id','Lines',required=True),
            'departure_date': fields.datetime('Departure Date'),
            'arrive_date': fields.datetime('Arrive Date'),
        }
    _defaults = {
            'state': 'draft',
            'name': '/'
        }
        
    def action_draft(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_draft(cr,uid,[line.id],context=context)
            
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
        
    def action_departure(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_delivered(cr,uid,[line.id],context=context)
            
        self.write(cr, uid, ids, {'state': 'departure','departure_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
        
    def action_arrive(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'arrive','arrive_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
        
    def action_done(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                if line.state in ('draft','delivered'):
                    raise osv.except_osv(_('Error'), _("The lines of delivery route mustn't be draft or delivered"))
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('delivery.route.line')
        for route in self.browse(cr,uid,ids,context=context):
            for line in route.line_ids:
                line_obj.action_cancel(cr,uid,[line.id],context=context)
            
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True
        
delivery_route()


class delivery_route_line(osv.osv):
    _name='delivery.route.line'
    _columns = {
            'sequence': fields.integer('Sequence'),
            'route_id': fields.many2one('delivery.route','Delivery Route', required=True, ondelete="cascade"),
            'picking_id': fields.many2one('stock.picking','Picking', required=True,select=True),
            'address_id': fields.related('picking_id','address_id',type='many2one',relation='res.partner.address',string='Delivery Address'),
            'state': fields.selection([
                                ('draft','Draft'),
                                ('delivered','Delivered'),
                                ('received','Received'),
                                ('returned','Returned'),
                                ('cancel','Cancel')],'State',readonly=True),
            'visit_date': fields.datetime('Visit Date',states={'delivered': [('required', True)],
                                                                'received':[('readonly',True)],
                                                                'returned':[('readonly',True)],}),
            'visit_note': fields.char('Visit Note',size=256,
                                states={'delivered': [('required', True)],
                                                                'received':[('readonly',True)],
                                                                'returned':[('readonly',True)],},
                                help="Fill field with the name of the person that receive the delivery or the reason for doesn't receive it."),
            'note': fields.text('Notes'),
        }
    _defaults = {
            'state': 'draft',
        }
    _order = 'sequence'

    def unlink(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), 
                        _('Cannot delete Delivery Route Line(s) which are already received, returned or delivered !'))
        return super(delivery_route_line, self).unlink(cr, uid, ids, context=context)

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def action_delivered_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr,uid,[line.picking_id.id],{'delivered':True},context=context)
        return True
        
    def action_delivered(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        for line in self.browse(cr,uid,ids,context=context):
            if line.picking_id.delivered:
                raise osv.except_osv(_('Error'), _('The picking %s (origin:%s) was delivered in other delivery route'%(line.picking_id.name,line.picking_id.origin)))
            if line.picking_id.state not in ('done'):
                raise osv.except_osv(_('Error'), _('The picking %s (origin:%s) must be in done state'%(line.picking_id.name,line.picking_id.origin)))
            self.action_delivered_do_line(cr, uid, line, context=context)
            
        self.write(cr, uid, ids, {'state': 'delivered'}, context=context)
        return True
        
    def action_received(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'received'}, context=context)
        return True
        
    def action_returned(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'returned'}, context=context)
        return True
        
    def action_cancel_do_line(self, cr, uid, line, context=None):
        self.pool.get('stock.picking').write(cr,uid,line.picking_id.id,{'delivered':False},context=context)
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            self.action_cancel_do_line(cr, uid, line, context=context)
            
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

delivery_route_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
