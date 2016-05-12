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
__version__ = "vocab_counter_test.py 2016-05-11T22:52-03:00"

# This file contains unit test for the vocab_counter function.
#
# Example:
#
# python vocab_counter_test.py

from vocab_counter import vocab_counter
from dwca_utils import read_header
import os
import unittest

class VocabCounterFramework():
    """Test framework for the vocab counter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_vocab_month.txt'

    # output data files from tests, remove these in dispose()
#    testvocabfile = testdatapath + 'test_vocab_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
#         testvocabfile = self.testvocabfile
#         if os.path.isfile(testvocabfile):
#             os.remove(testvocabfile)
        return True

class VocabCounterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = VocabCounterFramework()

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
        testfile = self.framework.testfile1

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=vocab_counter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs['inputfile'] = testfile
        response=vocab_counter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without termname'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['termname'] = 'year'
        response=vocab_counter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

    def test_term_exists(self):
        print 'testing term_exists'
        testfile = self.framework.testfile1

        header = read_header(testfile)
        term = 'year'
        present = term in header
        s = 'test file %s does not contain "%s" field' % (testfile, term)
        self.assertTrue(present, s)

        term = 'fieldNumber '
        present = term in header
        s = 'test file %s does not contain "%s" field' % (testfile, term)
        self.assertTrue(present, s)

        testfile = self.framework.testfile2
        header = read_header(testfile)
        term = 'verbatim'
        present = term in header
        s = 'test file %s does not contain "%s" field' % (testfile, term)
        self.assertTrue(present, s)

    def test_vocab_counter(self):
        print 'testing vocab_counter'
        testfile = self.framework.testfile1
        term = 'year'
        
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termname'] = term

        # Extract distinct values of term
#        print 'inputs:\n%s' % inputs
        response=vocab_counter(inputs)
#        print 'response:\n%s' % response
        values = response['extractedvalues']
        s = 'values of term %s not extracted correctly from %s' % (term, testfile)
        self.assertEqual(len(response['extractedvalues']), 4, s)
        y, c = response['extractedvalues'][0]
        self.assertEqual(y, '1990', s)
        self.assertEqual(c, 5, s)
        self.assertEqual(c, 5, s)

if __name__ == '__main__':
    print '=== vocab_counter_test.py ==='
    unittest.main()
