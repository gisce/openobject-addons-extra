# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account move CSV import module for OpenERP
#    Copyright (C) 2012 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
from datetime import datetime
import csv, codecs
import sys
import base64
from tempfile import TemporaryFile
import logging

_logger = logging.getLogger(__name__)

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.DictReader(f, **kwds)

    def next(self):
        row = self.reader.next()
#        print "next row=", row
        res = {}
        for key, value in row.items():
            if value and key:
                res[unicode(key, 'utf-8')] = unicode(value, 'utf-8')
            elif key:
                res[unicode(key, 'utf-8')] = value
            else:
                res[key] = value
        return res

    def __iter__(self):
        return self


class account_move_import(osv.osv_memory):
    _name = "account.move.import"
    _description = "Import account move from CSV file"

    def run_import_generic_csv(self, cr, uid, ids, context=None):
        setup = {}
        setup.update({
            'encoding': 'utf-8',
            'delimiter': ',',
            'quotechar': '"',
            'quoting' : csv.QUOTE_MINIMAL,
            'fieldnames': ['date', 'journal', 'account',
                    'analytic', 'label', 'debit', 'credit'],
            'date_format': '%d/%m/%Y',
            'top_lines_to_skip': 0, # Empty lines should not be counted ; they are automatically skipped
        })
        res = self.run_import_generic(cr, uid, ids, setup, context=context)
        return res

    def run_import_meilleuregestion(self, cr, uid, ids, context=None):
        setup = {}
        setup.update({
            'encoding': 'latin1',
            'delimiter': ';',
            'quoting' : csv.QUOTE_NONE,
            'fieldnames': ['trash1', 'trash2', 'trash3', 'trash4', 'trash5', 'account', 'date',
                    'trash6', 'analytic', 'trash7', 'trash8', 'trash9', 'journal', 'label',
                    'label2', 'sign', 'amount', 'debit', 'credit'],
            'date_format': '%d/%m/%Y',
            'top_lines_to_skip': 2, # Empty lines should not be counted ; they are automatically skipped
        })
        res = self.run_import_generic(cr, uid, ids, setup, context=context)
        return res

    def run_import_generic(self, cr, uid, ids, setup, context=None):
        import_data = self.browse(cr, uid, ids[0])
        _logger.info('Starting to import CSV file')
        # Code inspired by module/wizard/base_import_language.py
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(import_data.file_to_import))
        fileobj.seek(0) # Import... il faut revenir au début !
        reader = UnicodeDictReader(
            fileobj,
            fieldnames = setup.get('fieldnames'),
            delimiter = setup.get('delimiter'),
            quoting = setup.get('quoting'),
            quotechar = setup.get('quotechar', None),
            encoding = setup.get('encoding', 'utf-8'),
            )
        date = None
        journal = None
        move_ref = False
        date_datetime = False
        move_lines = 0
        lines = 0
        line_seq = []
        top_lines_to_skip = setup.get('top_lines_to_skip', 0)
        for row in reader:
            lines +=1
            print "lines=", lines
            if lines <= top_lines_to_skip:
                print "row=", row
                _logger.info('[line %d] Top line skipped' % lines)
                continue
            _logger.info('[line %d] Content : %s' % (lines, row))
            # Date and journal are read from the first line
            if not date_datetime:
                date_datetime = datetime.strptime(row['date'], setup.get('date_format'))
            if not journal:
                journal = row['journal']
            if not move_ref:
                move_ref = row['label']

            if row['analytic']:
                analytic_search = self.pool.get('account.analytic.account').search(cr, uid,
                    [('code', '=', row['analytic'])], context=context)
                if len(analytic_search) <> 1:
                    raise osv.except_osv('Error :', "No match for analytic account code '%s' (line %d of the CSV file)" % (row['analytic'], lines))
                analytic_account_id = analytic_search[0]
            else:
                analytic_account_id = False
            account_search = self.pool.get('account.account').search(cr, uid,
                [('code', '=', row['account'])], context=context)
            if len(account_search) <> 1:
                raise osv.except_osv('Error :', "No match for legal account code '%s' (line %d of the CSV file)" % (row['account'], lines))
            account_id = account_search[0]
            try:
                if row['debit']:
                    debit = float(row['debit'])
                else:
                    debit = 0
                if row['credit']:
                    credit = float(row['credit'])
                else:
                    credit = 0
            except:
                raise osv.except_osv('Error :', "Check that the decimal separator for the 'Debit' and 'Credit' columns is a dot")
            # If debit and credit = 0, we skip the move line
            if not debit and not credit:
                _logger.info('[line %d] Skipped because debit=credit=0' % lines)
                continue

            line_seq.append((0, 0, {
                'account_id': account_id,
                'name': row['label'],
                'debit': debit,
                'credit': credit,
                'analytic_account_id': analytic_account_id,
            }))
            move_lines += 1

        if not date_datetime:
            raise osv.except_osv('Error :', "No account move found in the CSV file")

        date_str = datetime.strftime(date_datetime, '%Y-%m-%d')
        journal_search = self.pool.get('account.journal').search(cr, uid, [('code', '=', journal)], context=context)
        if len(journal_search) <> 1:
            raise osv.except_osv('Error :', "No match for journal code '%s'" % journal)
        journal_id = journal_search[0]
        period_search = self.pool.get('account.period').find(cr, uid, date_str, context=context)
        if len(period_search) <> 1:
            raise osv.except_osv('Error :', "No matching period for date '%s'" % date_str)
        period_id = period_search[0]

        move_id = self.pool.get('account.move').create(cr, uid, {
            'journal_id': journal_id,
            'date': date_str,
            'period_id': period_id,
            'ref': move_ref, # in v6.1, 'name' <-> 'Number' -> do not fill !
            'line_id': line_seq,
            }, context=context)
        _logger.info('Account move ID %d created with %d move lines' % (move_id, move_lines))
        fileobj.close()

        res_validate = self.pool.get('account.move').validate(cr, uid, [move_id], context=context)
        _logger.info('Account move ID %d validated' % (move_id))
        if import_data.post_move:
            res_post = self.pool.get('account.move').post(cr, uid, [move_id], context=context)
            _logger.info('Account move ID %d posted' % (move_id))
        action = {
            'name': 'Account move',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': [move_id],
                }
        return action


    _columns = {
        'file_to_import': fields.binary('File to import', required=True, help="CSV file containing the account move to import."),
        'post_move': fields.boolean('Validate the account move', help="If True, the account move will be posted after the import."),
    }

account_move_import()
