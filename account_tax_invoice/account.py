# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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


class account_fiscalyear(osv.osv):
    _name = "account.fiscalyear"
    _inherit = "account.fiscalyear"
    _columns = {
            'fiscal_unit': fields.float('Fiscal Unit', help="A Fiscal Unit such as colombian UVT or peruvian UIT"),
        }
    
account_fiscalyear()


class account_tax_code(osv.osv):
    _name = "account.tax.code"
    _inherit = "account.tax.code"
    _columns = {
            'python_invoice': fields.text('Invoice Python Code',help='Python code to apply or not the tax at invoice level'),
            'applicable_invoice': fields.boolean('Applicable Invoice', help='Use python code to apply this tax code at invoice'),
        }

    _defaults = {
            'python_invoice': '''# amount\n# base\n# fiscal_unit\n# invoice: account.invoice object or False# address: res.partner.address object or False\n# partner: res.partner object or None\n# table: base.element object or None\n\n#result = table.get_element_percent(cr,uid,'COD_TABLE','COD_ELEMENT')/100\n#result = base > fiscal_unit * 4\n\nresult = True''',
            'applicable_invoice': False,
        }
    _order = 'sequence'
    
    def _applicable_invoice(self, cr, uid, tax_code_id, invoice_id, amount, base, context=None):
        localdict = {'amount':amount, 'base':base , 'cr': cr, 'uid': uid, 'table': self.pool.get('base.element')}
        code = self.browse(cr, uid, tax_code_id, context=context)
        if code.applicable_invoice:
            invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
            
            fiscal_unit = 0.0
            ctx = context.copy()
            ctx.update({'company_id': invoice.company_id.id})
            fiscalyear_obj = self.pool.get('account.fiscalyear')
                
            if invoice.period_id:
                fiscal_unit = invoice.period_id.fiscalyear_id.fiscal_unit
            else:
                fiscalyear_ids = fiscalyear_obj.find(cr, uid, invoice.date_invoice or fields.date.context_today(self,cr,uid,context=ctx), context=ctx)
                fiscalyear = fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context)
                fiscal_unit = fiscalyear.fiscal_unit
            
            localdict['fiscal_unit'] = fiscal_unit
            localdict['invoice'] = invoice
            localdict['address'] = invoice.address_invoice_id
            localdict['partner'] = invoice.partner_id
            exec code.python_invoice in localdict
        return localdict.get('result', True)

account_tax_code()


class account_invoice_tax(osv.osv):
    _name = "account.invoice.tax"
    _inherit = "account.invoice.tax"
    
    def compute(self, cr, uid, invoice_id, context=None):
        obj_tax = self.pool.get('account.tax.code')
        tax_grouped = super(account_invoice_tax,self).compute(cr, uid, invoice_id, context)
        for k in tax_grouped.keys():
            apply = True
            if k[0]:
                apply = obj_tax._applicable_invoice(cr, uid, k[0], invoice_id, tax_grouped[k]['amount'], tax_grouped[k]['base'], context=context)
            if k[1]:
                apply = apply and obj_tax._applicable_invoice(cr, uid, k[1], invoice_id, tax_grouped[k]['amount'], tax_grouped[k]['base'],context=context)
            if not apply:
                tax_grouped.pop(k)
            
        return tax_grouped

account_invoice_tax()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
