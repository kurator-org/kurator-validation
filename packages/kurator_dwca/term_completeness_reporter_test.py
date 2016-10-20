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
__version__ = "term_completeness_reporter_test.py 2016-10-20T16:30+02:00"

# This file contains unit tests for the term_completeness_reporter function.
#
# Example:
#
# python term_completeness_reporter_test.py

from term_completeness_reporter import term_completeness_reporter
from dwca_utils import read_header
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import read_csv_row
from dwca_utils import count_rows
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

class TermCompletenessReporterFramework():
    """Test framework for the text file filter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testinputfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testreportfile = 'test_term_completeness_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testdatapath+self.testreportfile
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        return True

class TermCompletenessReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TermCompletenessReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testinputfile = self.framework.testinputfile
        self.assertTrue(os.path.isfile(testinputfile), testinputfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=term_completeness_reporter(inputs)
        #print 'response1:\n%s' % response
        s = 'Success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['outputfile'] = testreportfile
        response=term_completeness_reporter(inputs)
        #print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['outputfile'] = testreportfile
        response=term_completeness_reporter(inputs)
        #print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_term_completeness_reporter(self):
        print 'testing term_completeness_reporter'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath
        outputfile = '%s/%s' % (workspace.rstrip('/'), testreportfile)
        
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['workspace'] = workspace
        inputs['outputfile'] = testreportfile

        # Create the report
        #print 'inputs:\n%s' % inputs
        response=term_completeness_reporter(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'Term completeness counter failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        #print 'response:\n%s' % response
        s = 'Output file %s not created' % outputfile
        self.assertTrue(os.path.isfile(outputfile), s)

        header = read_header(outputfile)

        rows = count_rows(outputfile)
        expected = 24
        s = 'Number of rows in %s ' % outputfile
        s += 'was %s, not as expected (%s) ' % (rows, expected)
        self.assertEqual(rows, expected, s)
        
        expected = ['field', 'count']
        s = 'Header: %s, not as expected: %s' % (header, expected)
        self.assertEqual(header, expected, s)
        
if __name__ == '__main__':
    print '=== term_completeness_reporter_test.py ==='
    unittest.main()
