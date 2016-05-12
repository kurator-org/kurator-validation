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
__version__ = "vocab_composite_extractor_test.py 2016-05-11T22:52-03:00"

# This file contains unit test for the vocab_composite_extractor function.
#
# Example:
#
# python vocab_composite_extractor_test.py

from vocab_composite_extractor import vocab_composite_extractor
import os
import unittest

class VocabCompositeExtractorFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
#    testvocabfile = testdatapath + 'test_vocab_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
#         testvocabfile = self.testvocabfile
#         if os.path.isfile(testvocabfile):
#             os.remove(testvocabfile)
        return True

class VocabCompositeExtractorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = VocabCompositeExtractorFramework()

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
        response=vocab_composite_extractor(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['termcomposite'] = 'year'
        response=vocab_composite_extractor(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs = {}
        inputs['inputfile'] = testfile
        response=vocab_composite_extractor(inputs)
#        print 'response3:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termcomposite'] = 'country|stateProvince'
        response=vocab_composite_extractor(inputs)
#        print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)

    def test_vocab_composite_extractor(self):
        print 'testing vocab_composite_extractor'
        testfile = self.framework.testfile1
        terms = 'country'

        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termcomposite'] = terms

        # Extract distinct values of term
        response=vocab_composite_extractor(inputs)
        values = response['valueset']
#        print '%s values: %s' % (term, values)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        self.assertEqual(values, ['United States'], s)

        terms = 'country|stateProvince'
        inputs['termcomposite'] = terms
        response=vocab_composite_extractor(inputs)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['United States|Colorado', 'United States|California', 
            'United States|Washington', 'United States|Hawaii'], s)

        terms = 'family '
        inputs['termcomposite'] = terms
        response=vocab_composite_extractor(inputs)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['Asteraceae ', 'Asteraceae  '], s)

        terms = 'country|stateProvince'
        testfile = self.framework.testfile2
        inputs['inputfile'] = testfile
        inputs['termcomposite'] = terms
        response=vocab_composite_extractor(inputs)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['Mozambique|Maputo', u'South Africa|Kwa-Zulu Natal'], s)

if __name__ == '__main__':
    print '=== vocab_composite_extractor_test.py ==='
    unittest.main()
