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
__version__ = "vocab_composite_appender_test.py 2016-02-21T20:11-03:00"

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
import json
import unittest

class VocabAppenderFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'

    # input data files to tests, don't remove these
    geogvocabfile = testdatapath + 'test_dwcgeography.txt'

    # output data files from tests, remove these in dispose()
    testvocabfile = testdatapath + 'test_composite_vocab.csv'

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
        self.assertFalse(os.path.isfile(testvocabfile), testvocabfile + ' exists. It should not for these tests.')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        geogvocabfile = self.framework.geogvocabfile

        inputs = {}
        response=json.loads(vocab_composite_appender(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['addedvalues'], \
            'values added without vocab file')
        self.assertFalse(response['success'], \
            'success without vocab file')

        inputs['vocabfile'] = geogvocabfile
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_composite_appender(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['addedvalues'], \
            'values added without added value list')
        self.assertFalse(response['success'], \
            'success with missing added values list')

        inputs['newvaluelist'] = None
#        print 'inputs:\n%s' % inputs
        response=json.loads(vocab_composite_appender(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['addedvalues'], \
            'values added without empty new values list')
        self.assertFalse(response['success'], \
            'no success with empty added values list')

    def test_vocab_composite_appender(self):
        print 'testing vocab_composite_appender'
        testvocabfile = self.framework.testvocabfile

        geogkey = compose_key_from_list(geogkeytermlist)
        n = [
            'Oceania|United States|US|Hawaii|Honolulu|Honolulu|North Pacific Ocean|Hawaiian Islands|Oahu',
            '|United States||WA|Chelan Co.||||'
            ]

        inputs = {}
        inputs['vocabfile'] = testvocabfile
        inputs['keyfields'] = geogkey
        inputs['newvaluelist'] = n
#        print 'inputs:\n%s' % inputs

        # Add new vocab to new vocab file
        response=json.loads(vocab_composite_appender(json.dumps(inputs)))
#        print 'response:\n%s' % response
        
        writtenlist = response['addedvalues']
#        print 'writtenlist1: %s' % writtenlist
        self.assertEqual(writtenlist, n, 'values not written to new testvocabfile')

        # Attempt to add same vocabs to the same vocabs file
        response=json.loads(vocab_composite_appender(json.dumps(inputs)))
        
        writtenlist = response['addedvalues']
#        print 'writtenlist2: %s' % writtenlist
        self.assertEquals(len(writtenlist), 0, 'duplicate value written to testvocabfile')
        
        header = read_header(testvocabfile)
#        print 'vocab file header:\n%s' % header
        self.assertEquals(header[0], geogkey, 'key field not correct in testvocabfile')

if __name__ == '__main__':
    unittest.main()