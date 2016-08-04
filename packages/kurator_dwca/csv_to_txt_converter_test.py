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
__version__ = "csv_to_txt_converter_test.py 2016-08-04T14:14+02:00"

# This file contains unit test for the csv_to_txt_converter function.
#
# Example:
#
# python csv_to_txt_converter_test.py

from csv_to_txt_converter import csv_to_txt_converter
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import dialects_equal
import os
import unittest

class CSVToTXTConverterFramework():
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

class CSVToTXTConverterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = CSVToTXTConverterFramework()

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
        response=csv_to_txt_converter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        response=csv_to_txt_converter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs = {}
        inputs['inputfile'] = testfile1
        response=csv_to_txt_converter(inputs)
#        print 'response4:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        response=csv_to_txt_converter(inputs)
#        print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_csv_to_txt_converter(self):
        print 'testing csv_to_txt_converter'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testdatapath = self.framework.testdatapath
        outputfile = self.framework.outputfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath

        # Translate the file to utf8 encoding
        response=csv_to_txt_converter(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        outdialect = csv_file_dialect(outfilelocation)
#        print 'inputs1:\n%s' % inputs
#        print 'response1:\n%s' % response
        equal = dialects_equal(outdialect, tsv_dialect())
        s = 'Output dialect for %s not TSV' % outfilelocation
        self.assertTrue(equal, s)

        inputs['inputfile'] = testfile2

        # Translate the file to utf8 encoding
        response=csv_to_txt_converter(inputs)
        outdialect = csv_file_dialect(outfilelocation)
#        print 'response2:\n%s' % response
        equal = dialects_equal(outdialect, tsv_dialect())
        s = 'Output dialect for %s not TSV' % outfilelocation
        self.assertTrue(equal, s)

if __name__ == '__main__':
    print '=== csv_to_txt_converter_test.py ==='
    unittest.main()
