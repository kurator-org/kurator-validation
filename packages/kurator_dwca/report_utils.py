#!/usr/bin/env python

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
__version__ = "report_utils.py 2016-09-19T13:53+02:00"

# This file contains common utility functions for dealing with the content of CSV and
# TSV data. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python report_utils.py

from dwca_utils import csv_dialect
from dwca_utils import tsv_dialect
from dwca_terms import vocabfieldlist
from dwca_vocab_utils import vocabheader
import logging
import unittest
import os.path
try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

def term_recommendation_report(reportfile, recommendationdict, key, separator='|', 
    format=None):
    """Write a term recommendation report.
    parameters:
        reportfile - full path to the output report file (optional)
        recommendationdict - dictionary of term recommendations (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        success - True if the report was written, else False
    """
#    print 'reportfile: %s\nrecommendationdict: %s' % (reportfile, recommendationdict)
    if recommendationdict is None or len(recommendationdict)==0:
        logging.debug('No term recommendations given in term_recommendation_report()')
        return False

    fieldnames = vocabheader(key, separator)

    if format=='csv' or format is None:
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    if reportfile is not None and len(reportfile)>0:
        with open(reportfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()

        if os.path.isfile(reportfile) == False:
            logging.debug('reportfile: %s not created' % reportfile)
            return False

        with open(reportfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            for datakey, value in recommendationdict.iteritems():
                row = {key:datakey, 
                    'standard':value['standard'], \
                    'vetted':value['vetted'], \
                    'error':value['error'], \
                    'misplaced':value['misplaced'], \
                    'unresolved':value['unresolved'], \
                    'source':value['source'], \
                    'comment':value['comment'] }
                fields = key.split(separator)
                if len(fields) > 1:
                    for field in fields:
                        row[field] = value[field]
                writer.writerow(row)
        logging.debug('Report written to %s in term_recommendation_report()' % reportfile)
    else:
        # Print the report to stdout
        print '%s\tstandard\tvetted\terror\tmisplaced\tunresolved\tsource\tcomment' % key
        for datakey, value in recommendationdict.iteritems():
            print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' ( \
                datakey,
                value['standard'], \
                value['vetted'], \
                value['error'], \
                value['misplaced'], \
                value['unresolved'], \
                value['source'], \
                value['comment'])
    return True

def term_list_report(reportfile, termlist, key, separator='|', format=None):
    """Write a report with a list of terms.
    parameters:
        reportfile - full path to the output report file (optional)
        termlist - list of terms to report (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        success - True if the report was written, else False
    """
#    print 'reportfile: %s\term_list_report: %s' % (reportfile, term_list_report)
    if termlist is None or len(termlist)==0:
        logging.debug('No term list given in term_list_report()')
        return False

    fieldnames = vocabheader(key, separator)

    if format=='csv' or format is None:
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    if reportfile is not None and len(reportfile)>0:
        with open(reportfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()

        if os.path.isfile(reportfile) == False:
            logging.debug('reportfile: %s not created' % reportfile)
            return False

        with open(reportfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            for value in termlist:
                row = {key:value, 
                    'standard':'', \
                    'vetted':'0', \
                    'error':'', \
                    'misplaced':'', \
                    'unresolved':'0', \
                    'source':'', \
                    'comment':'' }
                fields = key.split(separator)
                if len(fields) > 1:
                    # print 'report row: %s' % row
                    # print 'fields: %s' % fields
                    for field in fields:
                        row[field] = value
                writer.writerow(row)
        logging.debug('Report written to %s in term_list_report()' % reportfile)
    else:
        # Print the report to stdout
        print '%s\tstandard\tvetted\terror\tmisplaced\tunresolved\tsource\tcomment' % key
        for value in termlist:
            print '%s' % value
    return True

class ReportUtilsFramework():
    # testdatapath is the location of the files to test with
    testdatapath = './data/tests/'

    # following are files used as input during the tests, don't remove these
    csvreadheaderfile = testdatapath + 'test_eight_specimen_records.csv'
    tsvreadheaderfile = testdatapath + 'test_three_specimen_records.txt'

    # following are files output during the tests, remove these in dispose()
    testtokenreportfile = testdatapath + 'test_token_report_file.txt'

    def dispose(self):
        testtokenreportfile = self.testtokenreportfile
        if os.path.isfile(testtokenreportfile):
            os.remove(testtokenreportfile)
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

        self.assertTrue(os.path.isfile(csvreadheaderfile), csvreadheaderfile + ' does not exist')
        self.assertTrue(os.path.isfile(tsvreadheaderfile), tsvreadheaderfile + ' does not exist')

if __name__ == '__main__':
    print '=== report_utils.py ==='
    unittest.main()
