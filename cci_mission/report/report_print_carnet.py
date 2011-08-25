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
import time
from report import report_sxw

class print_carnet_header(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_header, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['header']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet1', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_header.rml', parser=print_carnet_header,header=False)

class print_carnet_export(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_export, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['export']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagenum':str(i),
                    'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet2', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_export.rml', parser=print_carnet_export,header=False)

class print_carnet_import(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_import, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['import']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagenum':str(i),
                    'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet3', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_import.rml', parser=print_carnet_import,header=False)

class print_carnet_transit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_transit, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['transit']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            if (i%2)==0:
                pagenum = str((i+1)//2)+'B'
            else:
                pagenum = str((i+1)//2)+'A'
            page = {'pagenum':pagenum,
                    'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet4', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_transit.rml', parser=print_carnet_transit,header=False)

class print_carnet_reexport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_reexport, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['reexport']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagenum':str(i),
                    'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet5', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_reexport.rml', parser=print_carnet_reexport,header=False)

class print_carnet_reimport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_reimport, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['reimport']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagenum':str(i),
                    'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet6', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_reimport.rml', parser=print_carnet_reimport,header=False)

class print_carnet_presence(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_presence, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['presence']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'cciname':carnet_obj.type_id.site_id.official_name_1,
                    'carnetname':carnet_obj.name,
                    'material':carnet_obj.usage_id.name,
                    'vyear':carnet_obj.validity_date[0:4],
                    'vmonth':carnet_obj.validity_date[5:7],
                    'vday':carnet_obj.validity_date[8:],
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet7', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_presence.rml', parser=print_carnet_presence,header=False)

class print_carnet_export_reimport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_export_reimport, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['export_reimport']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagea':str((i*2)-1),
                    'pageb':str(i*2),
                    'carnetname':carnet_obj.name,
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet8', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_export_reimport.rml', parser=print_carnet_export_reimport,header=False)

class print_carnet_import_reexport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_import_reexport, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['import_reexport']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagea':str((i*2)-1),
                    'pageb':str(i*2),
                    'carnetname':carnet_obj.name,
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet9', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_import_reexport.rml', parser=print_carnet_import_reexport,header=False)

class print_carnet_vtransit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(print_carnet_vtransit, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,'get_pages':self._get_pages})
    def _get_pages(self, form, objects):
        nbre_pages = form['vtransit']
        carnet_obj = objects[0]
        pages = []
        for i in range(1,nbre_pages+1):
            page = {'pagea':str((i*2)-1)+'A',
                    'pageb':str((i*2)-1)+'B',
                    'pagec':str(i*2)+'A',
                    'paged':str(i*2)+'B',
                    'carnetname':carnet_obj.name,
                   }
            pages.append(page)
        return pages
report_sxw.report_sxw('report.cci_missions_print_carnet10', 'cci_missions.ata_carnet', 'addons/cci_mission/report/report_print_carnet_vtransit.rml', parser=print_carnet_vtransit,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

