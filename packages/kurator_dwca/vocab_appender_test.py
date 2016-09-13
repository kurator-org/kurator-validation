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
__version__ = "vocab_appender_test.py 2016-09-12T11:58+02:00"

# This file contains unit test for the vocab_appender function.
#
# Example:
#
# python vocab_appender_test.py

from vocab_appender import vocab_appender
from dwca_utils import read_header
from dwca_utils import extract_values_from_file
from dwca_vocab_utils import compose_key_from_list
from dwca_terms import geogkeytermlist
import os
import unittest

class VocabAppenderFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    geogvocabfile = testdatapath + 'test_geography.txt'

    # output data files from tests, remove these in dispose()
    testvocabfile = testdatapath + 'test_vocab.csv'

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
        response=vocab_appender(inputs)
        # print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing key
        inputs['vocabfile'] = geogvocabfile
        response=vocab_appender(inputs)
        # print 'response2:\n%s' % response
        s = 'success without key'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs = {}
        s = 'continent|country|countrycode|stateprovince|'
        s += 'county|municipality|waterbody|islandgroup|island'
        inputs['key'] = s
        response=vocab_appender(inputs)
        # print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['vocabfile'] = geogvocabfile
        response=vocab_appender(inputs)
        # print 'response4:\n%s' % response
        s = 'values added with empty checkvalues list'
        self.assertIsNone(response['addedvalues'], s)
        s = 'success with empty checkvalues list'
        self.assertFalse(response['success'], s)

    def test_vocab_appender(self):
        print 'testing vocab_appender'
        testvocabfile = self.framework.testvocabfile

        geogkey = compose_key_from_list(geogkeytermlist)

        g1 = 'Oceania|United States|US|Hawaii|Honolulu|Honolulu|'
        g1 += 'North Pacific Ocean|Hawaiian Islands|Oahu'
        g2 = '|United States||WA|Chelan Co.||||'

        n = [g1, g2]

        inputs = {}
        inputs['vocabfile'] = testvocabfile
        inputs['key'] = geogkey
        inputs['checkvaluelist'] = n
        # print 'inputs:\n%s' % inputs

        # Add new vocab to new vocab file
        response=vocab_appender(inputs)
        # print 'response1:\n%s' % response
        
        writtenlist = response['addedvalues']
        # print 'writtenlist1: %s' % writtenlist
        self.assertEqual(writtenlist, n, 'values not written to new testvocabfile')

        header = read_header(testvocabfile)
        #print 'vocab file header:\n%s' % header

        # Attempt to add same vocabs to the same vocabs file
        response=vocab_appender(inputs)
        # print 'response2:\n%s' % response
        
        writtenlist = response['addedvalues']
        # print 'writtenlist2: %s' % writtenlist
        self.assertIsNone(writtenlist, 'duplicate value written to testvocabfile')
        
        header = read_header(testvocabfile)
        # print 'vocab file header:\n%s' % header
        self.assertEquals(header[0], geogkey, 'key field not correct in testvocabfile')

    def test_vocab_appender2(self):
        print 'testing vocab_appender2'
        testvocabfile = self.framework.testvocabfile
        checkvaluelist = ['May', 'v', '5', 'MAY']
        key = 'month'
        
        inputs = {}
        inputs['vocabfile'] = testvocabfile
        inputs['checkvaluelist'] = checkvaluelist
        inputs['key'] = key
        # print 'inputs: %s' % inputs

        # Aggregate all vocabs to new vocab file
        response=vocab_appender(inputs)
        # print 'response: %s' % response
        
        writtenlist = response['addedvalues']
        expected = ['5', 'MAY', 'May', 'v']
        s = 'To file: %s\n' % testvocabfile
        s += 'The verbatim values written: %s ' % writtenlist
        s += 'not as expected: %s' % expected
        self.assertEqual(writtenlist, expected, s)

        months = extract_values_from_file(testvocabfile, ['month'])
        expected = ['5', 'MAY', 'May', 'v']
        s = 'From file: %s\n' % testvocabfile
        s += 'The verbatim values read: %s ' % months
        s += 'not as expected: %s' % expected
        self.assertEqual(months, expected, s)

        checkvaluelist = ['vi', '6', 'June', 'JUNE']
        inputs['checkvaluelist'] = checkvaluelist
        # print 'inputs: %s' % inputs

        # Aggregate new vocabs to existing vocab file
        response=vocab_appender(inputs)
        # print 'response: %s' % response

        writtenlist = response['addedvalues']
        # print 'writtenlist2: %s' % writtenlist
        expected = ['6', 'JUNE', 'June', 'vi']
        s = 'To file: %s\n' % testvocabfile
        s += 'The verbatim values written: %s ' % writtenlist
        s += 'not as expected: %s' % expected
        self.assertEqual(writtenlist, expected, s)

        months = extract_values_from_file(testvocabfile, ['month'])
        expected = ['5', '6', 'JUNE', 'June', 'MAY', 'May', 'v', 'vi']
        s = 'From file: %s\n' % testvocabfile
        s += 'The verbatim values read: %s ' % months
        s += 'not as expected: %s' % expected
        self.assertEqual(months, expected, s)

if __name__ == '__main__':
    print '=== vocab_appender_test.py ==='
    unittest.main()
