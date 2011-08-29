# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010 Alexis de Lattre <alexis@via.ecp.fr>
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

from osv import osv, fields
# Lib required to open a socket (needed to communicate with Asterisk server)
#import socket
import urllib
# Lib required to print logs
import netsvc
# Lib to translate error messages
from tools.translate import _
# Lib for regexp
#import re


class escaux_server(osv.osv):
    '''Escaux server object, to store all the parameters of the ESCAUX SOP IPBXs'''
    _name = "escaux.server"
    _description = "Escaux Servers"
    _columns = {
        'name': fields.char('Escaux server name', size=50, required=True, help="Escaux SOP comprehensive server name."),
        'active': fields.boolean('Active', help="The active field allows you to hide the Escaux server without deleting it."),
        'ip_address': fields.char('Escaux IP addr. or DNS', size=50, required=True, help="IPv4 address or DNS name of the Escaux server."),
        'port': fields.integer('Port', required=True, help="TCP port on which the Escaux SOP listens."),
        'wait_time': fields.integer('Wait time (sec)', required=True, \
            help="Amount of time (in seconds) Escaux will try to reach the user's phone before hanging up."),
        'company_id': fields.many2one('res.company', 'Company', help="Company who uses the Escaux server."),
        'prefix_incoming' : fields.char('Prefix incoming',size=10, help="number added to the usual number for the incoming call (often '0')."),
        'prefix_outcoming' : fields.char('Prefix outcoming',size=10, help="number added to the phone number recorded in database before going out (often '0')."),
    }
    _defaults = {
        'active': lambda *a: True,
        'port': lambda *a: 80,
        'wait_time': lambda *a: 15,
    }

    def _check_wait_time(self, cr, uid, ids):
        for i in ids:
            wait_time_to_check = self.read(cr, uid, i, ['wait_time'])['wait_time']
            if wait_time_to_check < 1 or wait_time_to_check > 120:
                return False
        return True

    def _check_port(self, cr, uid, ids):
        for i in ids:
            port_to_check = self.read(cr, uid, i, ['port'])['port']
            if port_to_check > 65535 or port_to_check < 1:
                return False
        return True

    _constraints = [
        (_check_wait_time, "You should enter a 'Wait time' value between 1 and 120 seconds", ['wait_time']),
        (_check_port, 'TCP ports range from 1 to 65535', ['port']),
    ]

    def dial(self, cr, uid, ids, erp_number, context=None):
        '''
        Send commands to Escaux Server to ring the phone with the external number given

        '''
        logger = netsvc.Logger()
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Check if the number to dial is not empty
        if not erp_number:
            raise osv.except_osv(_('Error :'), _('There is no phone number to call !'))
        # Note : if I write 'Error' without ' :', it won't get translated...
        # Alexis de Lattre doesn't understand why ! I agree ...

        # We check if the user has an Escaux server configured
        if not user.escaux_server_id.id:
            raise osv.except_osv(_('Error :'), _('No Escaux server configured for the current user.'))
        else:
            escaux_server = user.escaux_server_id

        # We check if the current user has an internal number
        if not user.sip_name:
            raise osv.except_osv(_('Error :'), _('No internal phone name configured for the current user'))

        # The user should also have a CallerID
        #if not user.callerid:
        #    raise osv.except_osv(_('Error :'), _('No callerID configured for the current user'))

        # Convert the phone number in the format that will be sent to Escaux
        # in our case, the phone number are all encoded with the format '043419191' or '043419191 (private)'
        pos_final_parenthesis = erp_number.rfind( ' (' )
        if pos_final_parenthesis > -1:
            erp_number = erp_number[0:pos_final_parenthesis]
        logger.notifyChannel('escaux', netsvc.LOG_DEBUG, 'User dialing : channel = ' + user.sip_name)
        logger.notifyChannel('escaux', netsvc.LOG_DEBUG, 'Escaux server [' + escaux_server.name + '] = ' + escaux_server.ip_address + ':' + str(escaux_server.port))
        logger.notifyChannel('escaux', netsvc.LOG_DEBUG, 'Destination number:'+erp_number)
        
        # Connect to the Escaux Manager Interface, using IPv6-ready code
        try:
            full_url = 'http://' + escaux_server.ip_address + '/xml/ccOriginate.php?' + urllib.urlencode([('phone_id',user.sip_name),('to',escaux_server.prefix_outcoming+erp_number)])
            logger.notifyChannel('escaux', netsvc.LOG_DEBUG, full_url)
            print 'Full_URL:'+full_url+"!"
            req_res = urllib.urlopen(full_url)
        except:
            logger.notifyChannel('escaux', netsvc.LOG_WARNING, "Click2dial failed : unable to connect to Escaux")
            raise osv.except_osv(_('Error :'), _("The connection from OpenERP to the Escaux server failed. Please check the configuration on OpenERP and on Escaux."))
escaux_server()


# Parameters specific for each user
class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'sip_name': fields.char('SIP Phone ID', size=15, help="User's phone name on Escaux SOP"),
        'escaux_server_id': fields.many2one('escaux.server', 'Escaux server', help="Escaux server on which the user's phone is connected."),
    }
res_users()

# this adds action click to dial to the phone field of res.partner.address
class res_partner_address(osv.osv):
    _name = "res.partner.address"
    _inherit = "res.partner.address"

    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner address view'''
        erp_number = self.read(cr, uid, ids, ['phone'], context=context)[0]['phone']
        self.pool.get('escaux.server').dial(cr, uid, ids, erp_number, context=context)
res_partner_address()

# this adds action click to dial to the phone field of res.partner.job
class res_partner_job(osv.osv):
    _name = "res.partner.job"
    _inherit = "res.partner.job"

    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner job view'''
        erp_number = self.read(cr, uid, ids, ['phone'], context=context)[0]['phone']
        self.pool.get('escaux.server').dial(cr, uid, ids, erp_number, context=context)
res_partner_job()

# this adds action click to dial to the mobile field of res.partner.contact
class res_partner_contact(osv.osv):
    _name = "res.partner.contact"
    _inherit = "res.partner.contact"

    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the partner contact view'''
        erp_number = self.read(cr, uid, ids, ['mobile'], context=context)[0]['mobile']
        self.pool.get('escaux.server').dial(cr, uid, ids, erp_number, context=context)
res_partner_contact()

# This module supports multi-company
class res_company(osv.osv):
    _name = "res.company"
    _inherit = "res.company"
    _columns = {
        'escaux_server_ids': fields.one2many('escaux.server', 'company_id', 'Escaux servers', help="List of Escaux servers.")
    }
res_company()
