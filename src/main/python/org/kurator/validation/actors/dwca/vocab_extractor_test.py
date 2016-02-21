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
__version__ = "vocab_extractor_test.py 2016-02-21T14:32-03:00"

# This file contains unit test for the vocab_extractor function.
#
# Example:
#
# python vocab_extractor_test.py

from vocab_extractor import vocab_extractor
from dwca_utils import read_header
from dwca_vocab_utils import distinct_term_values_from_file
import os
import json
import unittest

class VocabExtractorFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'

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

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile = self.framework.testfile1

        inputs = {}
        response=json.loads(vocab_extractor(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['extractedvalues'], \
            'values extracted without input file')
        self.assertFalse(response['success'], \
            'success without input file')

        inputs['inputfile'] = testfile
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_extractor(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['extractedvalues'], \
            'values added without term name')
        self.assertFalse(response['success'], \
            'success with missing term name')

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

    def test_vocab_extractor(self):
        print 'testing vocab_extractor'
        testfile = self.framework.testfile1
        term = 'year'
        
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termname'] = term

        # Extract distinct values of term
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_extractor(json.dumps(inputs)))
#        print 'response:\n%s' % response
        values = response['extractedvalues']
        s = 'values of term %s not extracted correctly from %s' % (term, testfile)
        self.assertEqual(values, ['1973', '1990', '2003', '2007'], s)

        term = 'fieldNumber '
        inputs['termname'] = term
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_extractor(json.dumps(inputs)))
        values = response['extractedvalues']
#        print 'response:\n%s' % response
        s = 'values of term %s not extracted correctly from %s' % (term, testfile)
        self.assertEqual(values, ['107702', '126', '1940', '2503', '2938', '2940', '3000', '606'], s)

        testfile = self.framework.testfile2
        term = 'verbatim'
        inputs['inputfile'] = testfile
        inputs['termname'] = term
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_extractor(json.dumps(inputs)))
        values = response['extractedvalues']
#        print 'response:\n%s' % response
        s = 'values of term %s not extracted correctly from %s' % (term, testfile)
        self.assertEqual(values, ['5', 'V', 'VI', 'Vi', 'v', 'vi'], s)

if __name__ == '__main__':
    unittest.main()
