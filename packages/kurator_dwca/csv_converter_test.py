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
__version__ = "csv_converter_test.py 2016-10-18T19:00+02:00"

# This file contains unit test for the csv_converter function.
#
# Example:
#
# python csv_converter_test.py

from csv_converter import csv_converter
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import csv_dialect
from dwca_utils import dialect_attributes
from dwca_utils import dialects_equal
import csv
import os
import unittest

class CSVConverterFramework():
    """Test framework for CSV to TXT Converter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_three_records_utf8_unix_lf.txt'
    testfile2 = testdatapath + 'test_thirty_records_latin_1_crlf.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_txt_from_csv_file.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        return True

class CSVConverterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = CSVConverterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile1 = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        testfile2 = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile2), testfile2 + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile1 = self.framework.testfile1
        outputfile = self.framework.outputfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=csv_converter(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        response=csv_converter(inputs)
        #print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs = {}
        inputs['inputfile'] = testfile1
        response=csv_converter(inputs)
        #print 'response4:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        response=csv_converter(inputs)
        #print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_csv_converter(self):
        print 'testing csv_converter'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testdatapath = self.framework.testdatapath
        outputfile = self.framework.outputfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath
        inputs['format'] = 'csv'

        # Translate the file to csv
        response=csv_converter(inputs)

        outfilelocation = '%s%s' % (testdatapath, outputfile)
        outdialect = csv_file_dialect(outfilelocation)
        #print 'inputs1:\n%s' % inputs
        #print 'response1:\n%s' % response

        found = outdialect.lineterminator
        expected =  '\r'
        if found == '\r\n':
            s = 'found lineterminator \\r\\n, not \\r'
        elif found == '\\n':
            s = 'found lineterminator \\n, not \\r'
        else:
            s = 'lineterminator not as expected (\\r)'
        self.assertEqual(found, expected, s)

        found = outdialect.delimiter
        expected = ','
        s = 'found delimiter %s, not %s' % (found, expected)
        self.assertEqual(found, expected, s)

        found = outdialect.escapechar
        expected = '\\'
        s = 'found escapechar %s, not %s' % (found, expected)
        self.assertEqual(found, expected, s)

        found = outdialect.quotechar
        expected = '"'
        s = 'found quotechar %s, not %s' % (found, expected)
        self.assertEqual(found, expected, s)

        found = outdialect.doublequote
        expected = False
        s = 'found doublequote %s, not %s' % (found, expected)
        self.assertFalse(found)

        found = outdialect.quoting
        expected  = csv.QUOTE_MINIMAL
        s = 'found quoting %s, not %s' % (found, expected)
        
        found = outdialect.skipinitialspace
        expected = True
        s = 'found skipinitialspace %s, not %s' % (found, expected)
        self.assertTrue(found)
        
        found = outdialect.strict
        expected = False
        s = 'found strict %s, not %s' % (found, expected)
        self.assertFalse(found)

if __name__ == '__main__':
    print '=== csv_converter_test.py ==='
    unittest.main()
