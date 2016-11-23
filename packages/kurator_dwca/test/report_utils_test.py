#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "John Wieczorek"
__copyright__ = "Copyright 2016 President and Fellows of Harvard College"
__version__ = "report_utils_test.py 2016-10-21T14:34+02:00"

# This file contains unit tests for the functions in dwca_vocab_utils.
#
# Example:
#
# python report_utils_test.py

from kurator_dwca.dwca_utils import csv_file_dialect
from kurator_dwca.dwca_utils import csv_file_encoding
from kurator_dwca.dwca_utils import read_header
from kurator_dwca.dwca_utils import read_rows
from kurator_dwca.report_utils import term_setter_report
from kurator_dwca.report_utils import term_standardizer_report
import os
import unittest

# Replace the system csv with unicodecsv. All invocations of csv will use unicodecsv,
# which supports reading and writing unicode streams.
try:
    import unicodecsv as csv
except ImportError:
    import warnings
    s = "The unicodecsv package is required.\n"
    s += "pip install unicodecsv\n"
    s += "$JYTHON_HOME/bin/pip install unicodecsv"
    warnings.warn(s)

class ReportUtilsFramework():
    # testdatapath is the location of the files to test with
    testdatapath = '../data/tests/'

    # following are files used as input during the tests, don't remove these
    csvreadheaderfile = testdatapath + 'test_eight_specimen_records.csv'
    tsvreadheaderfile = testdatapath + 'test_three_specimen_records.txt'
    testcorrectioninputfile = testdatapath + 'test_specimen_correction.txt'
    testsetterinputfile = testdatapath + 'test_specimen_correction.txt'
    testmonthvocabfile = testdatapath + 'test_month.txt'

    # following are files output during the tests, remove these in dispose()
    testtokenreportfile = testdatapath + 'test_token_report_file.txt'
    testcorrectionreportfile = testdatapath + 'test_correction_report_file.txt'
    testsetterreportfile = testdatapath + 'test_setter_report_file.txt'

    def dispose(self):
        testtokenreportfile = self.testtokenreportfile
        testcorrectionreportfile = self.testcorrectionreportfile
        testsetterreportfile = self.testsetterreportfile
        if os.path.isfile(testtokenreportfile):
            os.remove(testtokenreportfile)
        if os.path.isfile(testcorrectionreportfile):
            os.remove(testcorrectionreportfile)
        if os.path.isfile(testsetterreportfile):
            os.remove(testsetterreportfile)
        return True

class ReportUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = ReportUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        csvreadheaderfile = self.framework.csvreadheaderfile
        tsvreadheaderfile = self.framework.tsvreadheaderfile
        testcorrectioninputfile = self.framework.testcorrectioninputfile

        s = csvreadheaderfile + ' does not exist'
        self.assertTrue(os.path.isfile(csvreadheaderfile), s)
        s = tsvreadheaderfile + ' does not exist'
        self.assertTrue(os.path.isfile(tsvreadheaderfile), s)
        s = testcorrectioninputfile + ' does not exist'
        self.assertTrue(os.path.isfile(testcorrectioninputfile), s)

    def test_term_setter_report(self):
        print 'testing term_setter_report'
        testsetterinputfile = self.framework.testsetterinputfile
        testsetterreportfile = self.framework.testsetterreportfile

        # Test field addition
        key = 'institutionCode'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='CAS')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country', 'institutionCode']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = csv_file_dialect(testsetterreportfile)
        encoding = csv_file_encoding(testsetterreportfile)
        rows = read_rows(testsetterreportfile, 1, dialect=dialect, encoding=encoding, 
            header=True, fieldnames=outputheader)
        firstrow = rows[0]

        field = 'institutionCode'
        value = firstrow[field]
        expected = 'CAS'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        # Test field list addition
        key = 'institutionCode|license'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='CAS|CC0')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country', 'institutionCode', 'license']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = csv_file_dialect(testsetterreportfile)
        encoding = csv_file_encoding(testsetterreportfile)
        rows = read_rows(testsetterreportfile, 1, dialect=dialect, encoding=encoding, 
            header=True, fieldnames=outputheader)
        firstrow = rows[0]

        field = 'institutionCode'
        value = firstrow[field]
        expected = 'CAS'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        field = 'license'
        value = firstrow[field]
        expected = 'CC0'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        # Test field replacement
        key = 'country'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='Argentina')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = csv_file_dialect(testsetterreportfile)
        encoding = csv_file_encoding(testsetterreportfile)
        rows = read_rows(testsetterreportfile, 1, dialect=dialect, encoding=encoding, 
            header=True, fieldnames=outputheader)
        firstrow = rows[0]

        field = 'country'
        value = firstrow[field]
        expected = 'Argentina'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

    def test_term_standardizer_report(self):
        print 'testing term_standardizer_report'
        testcorrectioninputfile = self.framework.testcorrectioninputfile
        testcorrectionreportfile = self.framework.testcorrectionreportfile
        testmonthvocabfile = self.framework.testmonthvocabfile
    
        key = 'month'
        result = term_standardizer_report(testcorrectioninputfile, \
            testcorrectionreportfile, testmonthvocabfile, key)
        s = 'term_standardizer_report() result not True '
        s += 'with inputfile: %s ' % testcorrectioninputfile
        s += 'outpufile: %s' % testcorrectionreportfile
        s += 'and vocabfile: %s' % testmonthvocabfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testcorrectionreportfile)
        expected = ['ID', 'month', 'country', 'month_orig']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = csv_file_dialect(testcorrectionreportfile)
        encoding = csv_file_encoding(testcorrectionreportfile)
        rows = read_rows(testcorrectionreportfile, 1, dialect=dialect, encoding=encoding, 
            header=True, fieldnames=outputheader)
        firstrow = rows[0]

        field = 'month_orig'
        value = firstrow[field]
        expected = 'vi'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        field = 'month'
        value = firstrow[field]
        expected = '6'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

if __name__ == '__main__':
    print '=== report_utils_test.py ==='
    unittest.main()
