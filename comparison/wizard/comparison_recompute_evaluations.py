# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv
from tools.translate import _
import netsvc

class comparison_recompute_evaluations(osv.osv_memory):
    _name = "comparison.recompute.evaluations"
    _description = "Evaluation Computation"
    
    def recompute(self, cr, uid, data, context):
        # This method re-calculates all the VOTED evaluations
#        pool = pooler.get_pool(cr.dbname)        
        obj_factor = self.pool.get('comparison.factor')
        obj_item = self.pool.get('comparison.item')
        obj_factor_result = self.pool.get('comparison.factor.result')
        
        #Itemwise calculation based on available votes will be easier
        item_ids = obj_item.search(cr, uid, [])
        #Setting all results and votes to 0.
        cr.execute('update comparison_factor_result set result=0.0,votes=0.0')
        
        for item in obj_item.browse(cr, uid, item_ids, context):
            parent_ids = []
            cr.execute(" select cf.id,cf.parent_id,sum(cvl.factor),count(cvl.factor) from comparison_vote as cv, \
                            comparison_factor cf,comparison_vote_values as cvl,comparison_item as ci where cv.state!='cancel' \
                            and cv.factor_id=cf.id and cf.state = 'open' and cv.item_id=ci.id and ci.id= %s and cv.score_id=cvl.id \
                            group by cf.id,cf.parent_id"%(item.id))
            res = cr.fetchall()
            # res : factor_id,parent_id, factor_name,sum(votes),no.of votes
            for record in res:
                #Re-compute all criterias
                if record[1] not in parent_ids:
                    parent_ids.append(record[1])
                
                score = (record[2] * 100)/ (float(record[3]) * 5.0)  # New score = total votes' score/no. of votes
                votes = record[3]
                result_id = obj_factor_result.search(cr, uid, [('factor_id','=',record[0]),('item_id','=',item.id)])
                if result_id:
                    obj_factor_result.write(cr, uid, result_id, {'result':score,'votes':votes})                  
            
            #re-compute upto top level
            for fact_id in parent_ids:
                factor = obj_factor.browse(cr, uid, fact_id) 
                
                while factor:
                    cr.execute("select sum(cf.ponderation) from comparison_factor as cf where cf.parent_id=%s and cf.state!='cancel'"%(factor.id))
                    tot_pond = cr.fetchall()
                    
                    cr.execute("select cfr.result,cf.ponderation,cfr.votes from comparison_factor_result as cfr,comparison_factor as cf where cfr.item_id=%s and cfr.votes > 0.0 and cfr.factor_id = cf.id and cf.parent_id=%s and cf.state!='cancel'"%(item.id,factor.id))
                    res1 = cr.fetchall()
                    final_score = 0.0
                    
                    votes = 1.0
                    if res1:
                        for record in res1:
                            votes = votes > record[2] and votes or record[2]
                            final_score += (record[0] * record[1])
            
                        final_score = final_score / tot_pond[0][0]   
                        parent_result_id = obj_factor_result.search(cr, uid, [('factor_id','=',factor.id),('item_id','=',item.id)])
                        obj_factor_result.write(cr, uid, parent_result_id[0],{'votes':votes,'result':final_score})
                            
                    factor = factor.parent_id or False
        
        return {'type': 'ir.actions.act_window_close'}


comparison_recompute_evaluations()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
