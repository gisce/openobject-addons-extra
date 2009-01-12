from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class Softwares(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.softwares")
    def index(self):
        
        userinfo = cherrypy.session.get('user_info', '')
        proxy = rpc.RPCProxy('comparison.item')
        
        ids = proxy.search([])        
        res = proxy.read(ids, ['name', 'note'])
            
        return dict(res=res, userinfo=userinfo)