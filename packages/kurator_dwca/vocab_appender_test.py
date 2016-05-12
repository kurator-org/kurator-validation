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
__version__ = "vocab_appender_test.py 2016-05-11T22:51-03:00"

# This file contains unit test for the vocab_appender function.
#
# Example:
#
# python vocab_appender_test.py

from vocab_appender import vocab_appender
from dwca_utils import read_header
from dwca_vocab_utils import distinct_term_values_from_file
import os
import unittest

class VocabAppenderFramework():
    """Test framework for the vocab loader."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    vocabfile = testdatapath + 'test_vocab_month.txt'

    # output data files from tests, remove these in dispose()
    testvocabfile = 'test_vocab_file.csv'

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

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        vocabfile = self.framework.vocabfile
        self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        vocabfile = self.framework.vocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=vocab_appender(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['vocabfile'] = vocabfile
        response=vocab_appender(inputs)
#        print 'response2:\n%s' % response
        s = 'values added no new values list'
        self.assertIsNone(response['addedvalues'], s)
        s = 'success without added values list'
        self.assertTrue(response['success'], s)

    def test_source_headers_correct(self):
        print 'testing source_headers_correct'
        vocabfile = self.framework.vocabfile

        header = read_header(vocabfile)
        modelheader = []
        modelheader.append('verbatim')
        modelheader.append('standard')
        modelheader.append('checked')
        modelheader.append('error')
        modelheader.append('misplaced')
        modelheader.append('incorrectable')
        modelheader.append('source')
        modelheader.append('comment')
#         print 'len(header): %s' % len(header)
#         print 'len(modelheader): %s' % len(modelheader)
#         print 'header:\n%s' % header
#         print 'model:\n%s' % modelheader
        self.assertEqual(len(header), 8, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_vocab_appender(self):
        print 'testing vocab_appender'
        testvocabfile = self.framework.testvocabfile
        checkvaluelist = ['May', 'v', '5', 'MAY']
        
        inputs = {}
        inputs['vocabfile'] = testvocabfile
        inputs['checkvaluelist'] = checkvaluelist

        # Aggregate all vocabs to new vocab file
        response=vocab_appender(inputs)
        
        writtenlist = response['addedvalues']
#        print 'inputs: %s\nresponse:\n%s' % (inputs, response)
        self.assertEqual(writtenlist, ['5', 'MAY', 'May', 'v'],
            'values not written to new testvocabfile')

        months = distinct_term_values_from_file(testvocabfile, 'verbatim')
        self.assertEqual(len(months), 4, 
            'the number of distinct verbatim values does not match expectation')
        self.assertEqual(months, ['5', 'MAY', 'May', 'v'],
            'verbatim month values do not match expectation')

        checkvaluelist = ['vi', '6', 'June', 'JUNE']
        inputs['checkvaluelist'] = checkvaluelist

        # Aggregate new vocabs to existing vocab file
        response=vocab_appender(inputs)

        writtenlist = response['addedvalues']
#        print 'writtenlist2: %s' % writtenlist
        self.assertEqual(writtenlist, ['6', 'JUNE', 'June', 'vi'],
            'new values not written to existing testvocabfile')

        months = distinct_term_values_from_file(testvocabfile, 'verbatim')
        self.assertEqual(len(months), 8, 
            'the number of distinct verbatim values does not match expectation after additions')
        self.assertEqual(months, ['5', '6', 'JUNE', 'June', 'MAY', 'May', 'v', 'vi'],
            'verbatim month values do not match expectation after addition')

if __name__ == '__main__':
    print '=== vocab_appender_test.py ==='
    unittest.main()
