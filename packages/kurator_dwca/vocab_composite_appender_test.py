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
__version__ = "vocab_composite_appender_test.py 2016-05-11T22:51-03:00"

# This file contains unit test for the vocab_composite_appender function.
#
# Example:
#
# python vocab_composite_appender_test.py

from vocab_composite_appender import vocab_composite_appender
from dwca_utils import read_header
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import compose_key_from_list
from dwca_terms import geogkeytermlist
import os
import unittest

class VocabAppenderFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    geogvocabfile = testdatapath + 'test_dwcgeography.txt'

    # output data files from tests, remove these in dispose()
    testvocabfile = 'test_composite_vocab.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testvocabfile = self.testvocabfile
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        return True

class VocabAppenderTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = VocabAppenderFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_temp_files_do_not_exist(self):
        print 'testing source_temp_files_do_not_exist'
        testvocabfile = self.framework.testvocabfile
        s = testvocabfile + ' exists. It should not for these tests.'
        self.assertFalse(os.path.isfile(testvocabfile), s)

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        geogvocabfile = self.framework.geogvocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=vocab_composite_appender(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing keyfields
        inputs['vocabfile'] = geogvocabfile
        response=vocab_composite_appender(inputs)
#        print 'response2:\n%s' % response
        s = 'success without keyfields'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs = {}
        s = 'continent|country|countrycode|stateprovince|'
        s += 'county|municipality|waterbody|islandgroup|island'
        inputs['keyfields'] = s
        response=vocab_composite_appender(inputs)
#        print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['vocabfile'] = geogvocabfile
        response=vocab_composite_appender(inputs)
#        print 'response4:\n%s' % response
        s = 'values added with empty checkvalues list'
        self.assertIsNone(response['addedvalues'], s)
        s = 'success with empty checkvalues list'
        self.assertFalse(response['success'], s)

    def test_vocab_composite_appender(self):
        print 'testing vocab_composite_appender'
        testvocabfile = self.framework.testvocabfile

        geogkey = compose_key_from_list(geogkeytermlist)

        g1 = 'Oceania|United States|US|Hawaii|Honolulu|Honolulu|'
        g1 += 'North Pacific Ocean|Hawaiian Islands|Oahu'
        g2 = '|United States||WA|Chelan Co.||||'

        n = [g1, g2]

        inputs = {}
        inputs['vocabfile'] = testvocabfile
        inputs['keyfields'] = geogkey
        inputs['checkvaluelist'] = n
#        print 'inputs:\n%s' % inputs

        # Add new vocab to new vocab file
        response=vocab_composite_appender(inputs)
#        print 'response:\n%s' % response
        
        writtenlist = response['addedvalues']
#        print 'writtenlist1: %s' % writtenlist
        self.assertEqual(writtenlist, n, 'values not written to new testvocabfile')

        # Attempt to add same vocabs to the same vocabs file
        response=vocab_composite_appender(inputs)
        
        writtenlist = response['addedvalues']
#        print 'writtenlist2: %s' % writtenlist
        self.assertEquals(len(writtenlist), 0, 'duplicate value written to testvocabfile')
        
        header = read_header(testvocabfile)
#        print 'vocab file header:\n%s' % header
        self.assertEquals(header[0], geogkey, 'key field not correct in testvocabfile')

if __name__ == '__main__':
    print '=== vocab_composite_appender_test.py ==='
    unittest.main()
