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
__version__ = "vocab_extractor_test.py 2016-09-08T16:18+02:00"

# This file contains unit test for the vocab_extractor function.
#
# Example:
#
# python vocab_extractor_test.py

from vocab_extractor import vocab_extractor
from dwca_utils import read_header
import os
import unittest

class VocabExtractorFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_vocab_month.txt'
    testfile3 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
#    testvocabfile = testdatapath + 'test_vocab_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
#         testvocabfile = self.testvocabfile
#         if os.path.isfile(testvocabfile):
#             os.remove(testvocabfile)
        return True

class VocabExtractorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = VocabExtractorFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile1 = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        testfile2 = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile2), testfile2 + ' does not exist')
        testfile3 = self.framework.testfile3
        self.assertTrue(os.path.isfile(testfile3), testfile3 + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile = self.framework.testfile1

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=vocab_extractor(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['terms'] = ['year']
        response=vocab_extractor(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing terms
        inputs = {}
        inputs['inputfile'] = testfile
        response=vocab_extractor(inputs)
#        print 'response3:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termlist'] = ['year']
        response=vocab_extractor(inputs)
#        print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)

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
        term = 'month'
        present = term in header
        s = 'test file %s does not contain "%s" field' % (testfile, term)
        self.assertTrue(present, s)

    def test_vocab_extractor(self):
        print 'testing vocab_extractor'
        testfile = self.framework.testfile1
        term = ['year']
        
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termlist'] = term

        # Extract distinct values of term
#        print 'inputs:\n%s' % inputs
        response=vocab_extractor(inputs)
#        print 'response:\n%s' % response
        values = response['extractedvalues']
        expected = ['1973', '1990', '2003', '2007']
        s = 'values of term %s\n%s\n' % (term, values)
        s += 'not as expected:\n%s' % expected
        self.assertEqual(values, expected, s)

        term = ['fieldNumber']
        inputs['termlist'] = term
#        print 'inputs:\n%s' % inputs
        response=vocab_extractor(inputs)
        values = response['extractedvalues']
#        print 'response:\n%s' % response
        s = 'values of term %s not extracted correctly from %s' % (term, testfile)
        v = ['107702', '126', '1940', '2503', '2938', '2940', '3000', '606']
        self.assertEqual(values, v, s)

        testfile = self.framework.testfile2
        term = ['month']
        inputs['inputfile'] = testfile
        inputs['termlist'] = term
#        print 'inputs:\n%s' % inputs
        response=vocab_extractor(inputs)
        values = response['extractedvalues']
        expected = ['5', '6', 'v', 'vi']
#        print 'response:\n%s' % response
        s = 'values of term %s:\n%s\n' % (term, values)
        s += 'not as expected: %s from %s' % (term, testfile)
        self.assertEqual(values, expected, s)

        testfile = self.framework.testfile1
        terms = ['country']

        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termlist'] = terms

        # Extract distinct values of term
        response=vocab_extractor(inputs)
#        print 'response1: %s' % response
        values = response['extractedvalues']
#        print '%s values: %s' % (term, values)
        expected = ['united states']
        s = 'country values: %s\n' % values
        s += 'do not match expectation: %s' % expected
        self.assertEqual(values, expected, s)

        terms = ['country', 'stateProvince']
        inputs['termlist'] = terms
        inputs['separator'] = '|'
        response=vocab_extractor(inputs)
        values = response['extractedvalues']
#        print 'values: %s' % values
        expected = [
            'united states|california', 
            'united states|colorado', 
            'united states|hawaii',
            'united states|washington'
            ]
        s = 'country|stateprovince values: %s\n' % values
        s += 'do not match expectation: %s' % expected
        self.assertEqual(values, expected, s)

        terms = ['family']
        inputs['termlist'] = terms
        inputs['separator'] = ''
        response=vocab_extractor(inputs)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['extractedvalues']
#        print 'values: %s' % values
        expected = ['asteraceae']
        s = 'family values: %s\n' % values
        s += 'do not match expectation: %s' % expected
        self.assertEqual(values, expected, s)

        terms = ['country', 'stateProvince']
        testfile = self.framework.testfile3
        inputs['inputfile'] = testfile
        inputs['termlist'] = terms
        inputs['separator'] = '|'
        response=vocab_extractor(inputs)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['extractedvalues']
#        print 'values: %s' % values
        expected = ['mozambique|maputo', u'south africa|kwa-zulu natal']
        s = 'country|stateprovince values: %s\n' % values
        s += 'do not match expectation: %s' % expected
        self.assertEqual(values, expected, s)

if __name__ == '__main__':
    print '=== vocab_extractor_test.py ==='
    unittest.main()
