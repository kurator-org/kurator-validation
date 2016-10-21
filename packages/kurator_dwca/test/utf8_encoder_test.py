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
__version__ = "utf8_encoder_test.py 2016-10-21T12:58+02:00"

# This file contains unit test for the utf8_encoder function.
#
# Example:
#
# python utf8_encoder_test.py

from kurator_dwca.utf8_encoder import utf8_encoder
from kurator_dwca.dwca_utils import csv_file_encoding
import os
import unittest

class UTF8EncoderFramework():
    """Test framework for UTF8 Encoder."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_records_utf8_lf.csv'
    testfile2 = testdatapath + 'test_thirty_records_latin_1_crlf.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_utf8encoded_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        return True

class UTF8EncoderTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = UTF8EncoderFramework()

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
        response=utf8_encoder(inputs)
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        response=utf8_encoder(inputs)
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs = {}
        inputs['inputfile'] = testfile1
        response=utf8_encoder(inputs)
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        response=utf8_encoder(inputs)
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_utf8_encoder(self):
        print 'testing utf8_encoder'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testdatapath = self.framework.testdatapath
        outputfile = self.framework.outputfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath

        # Translate the file to utf8 encoding
        response=utf8_encoder(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        encoding = csv_file_encoding(outfilelocation)
        expected = 'utf-8'
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, encoding, expected)
        self.assertEqual(encoding, expected, s)

        inputs['inputfile'] = testfile2

        # Translate the file to utf8 encoding
        response=utf8_encoder(inputs)
        encoding = csv_file_encoding(outfilelocation)
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile2, encoding, expected)
        self.assertEqual(encoding, expected, s)

        inputs['encoding'] = 'mac_roman'

        # Translate the file to utf8 encoding
        response=utf8_encoder(inputs)
        encoding = csv_file_encoding(outfilelocation)
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile2, encoding, expected)
        self.assertEqual(encoding, expected, s)

if __name__ == '__main__':
    print '=== utf8_encoder_test.py ==='
    unittest.main()
