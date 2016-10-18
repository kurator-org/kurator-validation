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
__version__ = "text_file_field_stripper_test.py 2016-10-18T22:34+02:00"

# This file contains unit tests for the text_file_field_stripper function.
#
# Example:
#
# python text_file_field_stripper_test.py

from text_file_field_stripper import text_file_field_stripper
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

class TextFileFieldStripperFramework():
    """Test framework for the text file filter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testinputfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testreportfile = 'test_tefile_filter_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testdatapath+self.testreportfile
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        return True

class TextFileFieldStripperTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TextFileFieldStripperFramework()

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
        response=text_file_field_stripper(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing termlist
        inputs['inputfile'] = testinputfile
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=text_file_field_stripper(inputs)
        #print 'response2:\n%s' % response
        s = 'success without termlist'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['termlist'] = 'country'
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=text_file_field_stripper(inputs)
        #print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['outputfile'] = testreportfile
        inputs['termlist'] = 'country'
        response=text_file_field_stripper(inputs)
        #print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_text_file_field_stripper(self):
        print 'testing text_file_field_stripper'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath
        outputfile = '%s/%s' % (workspace.rstrip('/'), testreportfile)
        termlist = 'country|stateProvince'
        
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termlist'] = termlist
        inputs['workspace'] = workspace
        inputs['outputfile'] = testreportfile
        inputs['separator'] = '|'

        # Create the report
        #print 'inputs:\n%s' % inputs
        response=text_file_field_stripper(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'text file filter failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        #print 'response:\n%s' % response
        s = 'Output file %s not created' % outputfile
        self.assertTrue(os.path.isfile(outputfile), s)

        header = read_header(outputfile)
        dialect = csv_file_dialect(outputfile)
        encoding = csv_file_encoding(outputfile)

        rows = count_rows(outputfile)
        expected = 10
        s = 'Number of rows in %s ' % outputfile
        s += 'was %s, not as expected (%s) ' % (rows, expected)
        self.assertEqual(rows, expected, s)
        
        expected = ['country', 'stateprovince']
        s = 'Header: %s, not as expected: %s' % (header, expected)
        self.assertEqual(header, expected, s)
        
if __name__ == '__main__':
    print '=== text_file_field_stripper_test.py ==='
    unittest.main()
