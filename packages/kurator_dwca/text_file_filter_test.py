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
__version__ = "text_file_filter_test.py 2016-10-04T16:36+02:00"

# This file contains unit tests for the text_file_filter function.
#
# Example:
#
# python text_file_filter_test.py

from text_file_filter import text_file_filter
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

class TextFileFilterFramework():
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

class TextFileFilterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TextFileFilterFramework()

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
        response=text_file_filter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs['inputfile'] = testinputfile
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=text_file_filter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without termname'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['termname'] = 'year'
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=text_file_filter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

        # Test with missing matchingvalue
        inputs = {}
        inputs['termname'] = 'year'
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        inputs['inputfile'] = testinputfile
        response=text_file_filter(inputs)
#        print 'response4:\n%s' % response
        s = 'success without matching value'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termname'] = 'year'
        inputs['matchingvalue'] = '1990'
        response=text_file_filter(inputs)
#        print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_text_file_filter(self):
        print 'testing text_file_filter'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath
        outputfile = '%s/%s' % (workspace.rstrip('/'), testreportfile)
        termname = 'year'
        matchingvalue = '1990'
        
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termname'] = termname
        inputs['matchingvalue'] = matchingvalue
        inputs['workspace'] = workspace
        inputs['outputfile'] = testreportfile

        # Create the report
#        print 'inputs:\n%s' % inputs
        response=text_file_filter(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'text file filter failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
#        print 'response:\n%s' % response
        s = 'Output file %s not created' % outputfile
        self.assertTrue(os.path.isfile(outputfile), s)

        header = read_header(outputfile)
        dialect = csv_file_dialect(outputfile)
        encoding = csv_file_encoding(outputfile)

        matches = 0
        # Iterate through all rows in the input file
        for row in read_csv_row(outputfile, dialect=dialect, encoding=encoding, 
            header=True, fieldnames=header):
            #print 'row: %s' % row
            if row[termname] == matchingvalue:
                matches +=1
        expected = 5
        s = 'Number of matches in output (%s) not as expected (%s)' % (matches, expected)
        self.assertEqual(matches, expected, s)

        matches = count_rows(outputfile)
        expected = 7
        s = 'Number of matches of %s in %s ' % (matchingvalue, outputfile)
        s += 'was %s, not as expected (%s) ' % (matches, expected)
        self.assertEqual(matches, expected, s)
        
if __name__ == '__main__':
    print '=== text_file_filter_test.py ==='
    unittest.main()
