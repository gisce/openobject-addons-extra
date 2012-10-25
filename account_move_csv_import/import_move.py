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
from pprint import pformat
from copy import deepcopy

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

    def run_import(self, cr, uid, ids, context=None):
        import_data = self.browse(cr, uid, ids[0], context=context)
        file_format = import_data.file_format
        if file_format == 'meilleuregestion':
            return self.run_import_meilleuregestion(cr, uid, import_data, context=context)
        elif file_format == 'genericcsv':
            return self.run_import_genericcsv(cr, uid, import_data, context=context)
        elif file_format == 'quadra':
            return self.run_import_quadra(cr, uid, import_data, context=context)
        else:
            raise osv.except_osv(_('Error :'), _("You must select a file format."))


    def run_import_genericcsv(self, cr, uid, import_data, context=None):
        setup = {}
        setup.update({
            'encoding': 'utf-8',
            'delimiter': ',',
            'quotechar': '"',
            'quoting' : csv.QUOTE_MINIMAL,
            'fieldnames': ['date', 'journal', 'account',
                    'analytic', 'label', 'debit', 'credit'],
            'date_format': '%d/%m/%Y',
            'top_lines_to_skip': 0,
            'bottom_lines_to_skip': 0,
        })
        account_move_dict = self.parse_csv(cr, uid, import_data, setup, context=context)
        action = self._generate_account_move(cr, uid, account_move_dict, setup, context=context)
        return action

    def run_import_meilleuregestion(self, cr, uid, import_data, context=None):
        setup = {}
        setup.update({
            'encoding': 'latin1',
            'delimiter': ';',
            'quoting' : csv.QUOTE_NONE,
            'fieldnames': ['trash1', 'trash2', 'trash3', 'trash4', 'trash5', 'account', 'date',
                    'trash6', 'analytic', 'trash7', 'trash8', 'trash9', 'journal', 'label',
                    'label2', 'sign', 'amount', 'debit', 'credit'],
            'date_format': '%d/%m/%Y',
            'top_lines_to_skip': 4,
            'bottom_lines_to_skip': 3,
        })
        account_move_dict = self.parse_csv(cr, uid, import_data, setup, context=context)
        action = self._generate_account_move(cr, uid, account_move_dict, setup, context=context)
        return action


    def run_import_quadra(self, cr, uid, import_data, context=None):
        setup = {}
        setup.update({
            'encoding': 'latin1',
            'date_format': '%d%m%y',
            'top_lines_to_skip': 0,
            'bottom_lines_to_skip': 0,
        })
        account_move_dict = self.parse_cols(cr, uid, import_data, setup, context=context)
        action = self._generate_account_move(cr, uid, account_move_dict, setup, context=context)
        return action

    def parse_common(self, cr, uid, import_data, setup, context=None):
        setup['post_move'] = import_data.post_move
        setup['force_journal_id'] = import_data.force_journal_id.id
        fullstr = base64.decodestring(import_data.file_to_import)
        if setup.get('bottom_lines_to_skip'):
            end_seq = -(setup.get('bottom_lines_to_skip') + 1)
        else:
            end_seq = None
        return fullstr, end_seq


    def parse_cols(self, cr, uid, import_data, setup, context=None):
        _logger.debug('Starting to import flat file')
        fullstr, end_seq = self.parse_common(cr, uid, import_data, setup, context=context)
        if setup.get('top_lines_to_skip') or setup.get('bottom_lines_to_skip'):
            cutstr = fullstr.split('\n')[setup.get('top_lines_to_skip'):end_seq]
            _logger.debug('%d top lines skipped' % setup.get('top_lines_to_skip'))
            _logger.debug('%d bottom lines skipped' % setup.get('bottom_lines_to_skip'))
        else:
            cutstr = fullstr.split('\n')
 
        move = []
        # 2nd parsing that updates top_lines_to_skip
        for line in cutstr:
            if not line:
                setup['top_lines_to_skip'] += 1
                continue
            elif line[0] == 'M':
                break
            else:
                setup['top_lines_to_skip'] += 1
        print "setup['top_lines_to_skip']=", setup['top_lines_to_skip']
        cutstr2 = fullstr.split('\n')[setup.get('top_lines_to_skip'):end_seq]
        print "cutstr2=", pformat(cutstr2)
        for line in cutstr2:
            # This should only be the case for the last line
            # TODO find why and fix
            if not line:
                continue
            line = line.strip()
            print "line=", line
            line_dict = {}
            line_dict['account'] = line[1:9]
            if line_dict['account'].isdigit():
                line_dict['account'] = line[1:7]
            else:
                line_dict['account'] = line[1:9].strip()
            line_dict['date'] = line[14:20]
            line_dict['label'] = line[21:41].strip().decode(setup.get('encoding'))
            print "amount_raw=", line[42:55]
            print "int amount_raw=", int(line[42:55])
            amount_raw = float(int(line[42:55]))
            amount = amount_raw/100
            if line[41] == 'C':
                line_dict['credit'] = amount
            else:
                line_dict['credit'] = 0
            if line[41] == 'D':
                line_dict['debit'] = amount
            else:
                line_dict['debit'] = 0
            line_dict['journal'] = line[9:11]
            line_dict['analytic'] = False
            print "line_dict=", line_dict
            move.append(line_dict)
        print "move=", pformat(move)
        print "len move=", len(move)
        return move

    def parse_csv(self, cr, uid, import_data, setup, context=None):
        _logger.debug('Starting to import CSV file')
        # Code inspired by module/wizard/base_import_language.py
        #print "Imported file=", base64.decodestring(import_data.file_to_import)
        fullstr, end_seq = self.parse_common(cr, uid, import_data, setup, context=context)
        if setup.get('top_lines_to_skip') or setup.get('bottom_lines_to_skip'):
            cutstr = '\n'.join(fullstr.split('\n')[setup.get('top_lines_to_skip'):end_seq])
            _logger.debug('%d top lines skipped' % setup.get('top_lines_to_skip'))
            _logger.debug('%d bottom lines skipped' % setup.get('bottom_lines_to_skip'))
        else:
            cutstr = fullstr
        fileobj = TemporaryFile('w+')
        setup['tempfile'] = fileobj
        fileobj.write(cutstr)
        fileobj.seek(0) # We must start reading from the beginning !
        reader = UnicodeDictReader(
            fileobj,
            fieldnames = setup.get('fieldnames'),
            delimiter = setup.get('delimiter'),
            quoting = setup.get('quoting'),
            quotechar = setup.get('quotechar', None),
            encoding = setup.get('encoding', 'utf-8'),
            )
#        fileobj.close() # TODO : re tester si ça marche qd
        return reader

    def _generate_account_move(self, cr, uid, account_move_dict, setup, context=None):
        date = None
        journal = False
        move_ref = False
        date_datetime = False
        line_csv = setup.get('top_lines_to_skip', 0)
        # moves_to_create contains a seq ; each member is a dict with keys journal, date, lines and ref
        moves_to_create = []
        move_ids_created = []
        move_dict_init = {
            'journal': False,
            'date_datetime': False,
            'ref': False,
            'lines': [],
            'balance': 0}
        move_dict = deepcopy(move_dict_init)

        for row in account_move_dict:
            line_csv +=1
            _logger.debug('[line %d] Content : %s' % (line_csv, row))
            # Date and journal are read from the first line
            if not move_dict['date_datetime']:
                move_dict['date_datetime'] = datetime.strptime(row['date'], setup.get('date_format'))
            if not move_dict['journal']:
                move_dict['journal'] = row['journal']
            if not move_dict['ref']:
                move_dict['ref'] = row['label']

            if row['analytic']:
                analytic_search = self.pool.get('account.analytic.account').search(cr, uid,
                    [('code', '=', row['analytic'])], context=context)
                if len(analytic_search) <> 1:
                    raise osv.except_osv('Error :', "No match for analytic account code '%s' (line %d of the CSV file)" % (row['analytic'], line_csv))
                analytic_account_id = analytic_search[0]
            else:
                analytic_account_id = False
            account_search = self.pool.get('account.account').search(cr, uid,
                [('code', '=', row['account'])], context=context)
            if len(account_search) <> 1:
                raise osv.except_osv('Error :', "No match for legal account code '%s' (line %d of the CSV file)" % (row['account'], line_csv))
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
                _logger.debug('[line %d] Skipped because debit=credit=0' % line_csv)
                continue

            line_dict = {
                'account_id': account_id,
                'name': row['label'],
                'debit': debit,
                'credit': credit,
                'analytic_account_id': analytic_account_id,
            }

            move_dict['lines'].append((0, 0, line_dict))
            move_dict['balance'] += debit - credit
            _logger.debug('[line %d] with this line, current balance is %d' % (line_csv, move_dict['balance']))
            print "debit=", debit
            print "credit=", credit
            print "move_dict['balance']=", move_dict['balance']
            if not int(move_dict['balance']*100):
                moves_to_create.append(move_dict)
                _logger.debug('[line %d] NEW account move' % line_csv)
                move_dict = deepcopy(move_dict_init)

        if setup.get('tempfile'):
            print "Close file descripor"
            setup.get('tempfile').close()

        for move_to_create in moves_to_create:
#TODO
#            if not date_datetime:
#               raise osv.except_osv('Error :', "No account move found in the CSV file")

            date_str = datetime.strftime(move_to_create['date_datetime'], '%Y-%m-%d')
            # If the user has forced a journal, we take it
            # otherwize, we take the journal of the CSV file
            if setup.get('force_journal_id'):
                journal_id = setup.get('force_journal_id')
            else:
                journal_search = self.pool.get('account.journal').search(cr, uid, [('code', '=', move_to_create['journal'])], context=context)
                if len(journal_search) <> 1:
                    raise osv.except_osv('Error :', "No match for journal code '%s'" % journal)
                journal_id = journal_search[0]

            # Select period
            period_search = self.pool.get('account.period').find(cr, uid, date_str, context=context)
            if len(period_search) <> 1:
                raise osv.except_osv('Error :', "No matching period for date '%s'" % date_str)
            period_id = period_search[0]

            # Create move
            move_id = self.pool.get('account.move').create(cr, uid, {
                'journal_id': journal_id,
                'date': date_str,
                'period_id': period_id,
                'ref': move_to_create['ref'], # in v6.1, 'name' <-> 'Number' -> do not fill !
                'line_id': move_to_create['lines'],
                }, context=context)
            _logger.debug('Account move ID %d created with %d move lines' % (move_id, len(move_to_create['lines'])))
            move_ids_created.append(move_id)

        res_validate = self.pool.get('account.move').validate(cr, uid, move_ids_created, context=context)
        _logger.debug('Account move IDs %s validated' % move_ids_created)
        if setup.get('post_move'):
            res_post = self.pool.get('account.move').post(cr, uid, move_ids_created, context=context)
            _logger.debug('Account move ID %s posted' % move_ids_created)

        action = {
            'name': 'Account move',
            'view_type': 'form',
            'view_id': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            }

        if len(move_ids_created) == 1:
            action.update({
                'view_mode': 'form,tree',
                'res_id': move_ids_created,
                })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', move_ids_created)],
                })
        return action


    _columns = {
        'file_to_import': fields.binary('File to import', required=True, help="CSV file containing the account move to import."),
        'post_move': fields.boolean('Validate the account move', help="If True, the account move will be posted after the import."),
        'force_journal_id': fields.many2one('account.journal', string="Force Journal", help="Journal in which the account move will be created, even if the CSV file indicate another journal."),
        'file_format': fields.selection([
            ('meilleuregestion', 'MeilleureGestion'),
            ('genericcsv', 'Generic CSV'),
            ('quadra', 'Quadra'),
            ], 'File format', help="Select the type of file you are importing."),
    }

account_move_import()
