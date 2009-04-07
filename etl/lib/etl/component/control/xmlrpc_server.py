# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
"""
 to run xmlrpc server

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""
from etl.component import component
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

class xmlrpc_server(component):
    """
    To connect server with xmlrpc request

    """
    def __init__(self, job, host='localhost', port=5000, name='control.xmlrpc_server', transformer=None):
        """
        To be update
        """
        super(xmlrpc_server, self).__init__(name, transformer=transformer)
        self.job = job
        self.host=host
        self.port=port
        self.datas=[]
        self.isStarted=False

    def start(self):
        self.isStarted=True
        server = SimpleXMLRPCServer((self.host, self.port))
        server.register_introspection_functions()
        server.register_function(self.import_data)        
        server.serve_forever()        

    def process(self):        
        if not self.isStarted:
            self.start()                
    

    def data_iterator(self,datas):
        for d in datas:
            yield d,'main'

    def import_data(self, datas):#to be check              
        if not self.job:
            return
        job=self.job.copy()                              
        if datas:                
            self.generator=self.data_iterator(datas)
            job.run()
        else:
            if job.status in ('start'):
                job.pause()        
        return True    

def test():
    pass
if __name__ == '__main__':
#    test()
    pass