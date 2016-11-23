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
__version__ = "term_counter_test.py 2016-10-21T12:28+02:00"

# This file contains unit test for the term_counter function.
#
# Example:
#
# python term_counter_test.py

from kurator_dwca.term_counter import term_counter
import os
import unittest

class TermCounterFramework():
    """Test framework for the term counter."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
    testvocabfile = testdatapath + 'test_vocab_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testvocabfile = self.testvocabfile
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        return True

class TermCounterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TermCounterFramework()

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
        response=term_counter(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs['inputfile'] = testfile
        response=term_counter(inputs)
        #print 'response2:\n%s' % response
        s = 'success without termname'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['termname'] = 'year'
        response=term_counter(inputs)
        #print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

    def test_term_counter(self):
        print 'testing term_counter'
        testfile = self.framework.testfile1
        termname = 'year'
        
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termname'] = termname

        # Extract distinct values of term
        response=term_counter(inputs)
        #print 'response:\n%s' % response
        rowcount = response['rowcount']
        expected = 8
        s = 'rowcount for term %s not extracted correctly from %s' % (termname, testfile)
        self.assertEqual(rowcount, expected, s)

        testfile = self.framework.testfile2
        term = 'island'
        inputs['inputfile'] = testfile
        inputs['termname'] = term
        response=term_counter(inputs)
        rowcount = response['rowcount']
        #print 'response:\n%s' % response
        s = 'rowcount for term %s not extracted correctly from %s' % (term, testfile)
        self.assertEqual(rowcount, 1, s)

if __name__ == '__main__':
    print '=== term_counter_test.py ==='
    unittest.main()
