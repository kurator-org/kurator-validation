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
__version__ = "vocab_composite_extractor_test.py 2016-02-12T12:31-03:00"

# This file contains unit test for the vocab_composite_extractor function.
#
# Example:
#
# python vocab_composite_extractor_test.py

from vocab_composite_extractor import vocab_composite_extractor
from dwca_utils import read_header
from dwca_vocab_utils import distinct_term_values_from_file
import os
import json
import unittest

class VocabCompositeExtractorFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'

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

    def test_vocab_composite_extractor(self):
        print 'testing vocab_composite_extractor'
        testfile = self.framework.testfile1
        terms = 'country'

        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termcomposite'] = terms

        # Extract distinct values of term
        response=json.loads(vocab_composite_extractor(json.dumps(inputs)))
        values = response['valueset']
#        print '%s values: %s' % (term, values)
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        self.assertEqual(values, ['United States'], s)

        terms = 'country|stateProvince'
        inputs['termcomposite'] = terms
        response=json.loads(vocab_composite_extractor(json.dumps(inputs)))
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['United States|Colorado', 'United States|California', 
            'United States|Washington', 'United States|Hawaii'], s)

        terms = 'family '
        inputs['termcomposite'] = terms
        response=json.loads(vocab_composite_extractor(json.dumps(inputs)))
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['Asteraceae ', 'Asteraceae  '], s)

        terms = 'country|stateProvince'
        testfile = self.framework.testfile2
        inputs['inputfile'] = testfile
        inputs['termcomposite'] = terms
        response=json.loads(vocab_composite_extractor(json.dumps(inputs)))
        s = 'values of key %s not extracted correctly from %s' % (terms, testfile)
        values = response['valueset']
#        print 'values: %s' % values
        self.assertEqual(values, ['Mozambique|Maputo', u'South Africa|Kwa-Zulu Natal'], s)

if __name__ == '__main__':
    unittest.main()
