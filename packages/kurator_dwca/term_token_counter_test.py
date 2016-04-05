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
__version__ = "term_token_counter_test.py 2016-04-05T14:19-03:00"

# This file contains unit test for the term_token_counter function.
#
# Example:
#
# python term_token_counter_test.py

from term_token_counter import term_token_counter
from dwca_utils import read_header
import os
import json
import unittest

class TermCounterFramework():
    """Test framework for the term counter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    termtokenfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testtokenextractfile = testdatapath + 'test_token_extract_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testtokenextractfile = self.testtokenextractfile
        if os.path.isfile(testtokenextractfile):
            os.remove(testtokenextractfile)
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
        termtokenfile = self.framework.termtokenfile
        self.assertTrue(os.path.isfile(termtokenfile), termtokenfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        termtokenfile = self.framework.termtokenfile

        inputs = {}
        response=json.loads(term_token_counter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['tokens'], \
            'tokens found without input file')
        self.assertFalse(response['success'], \
            'success without input file')

        inputs['inputfile'] = termtokenfile
#        print 'inputs:\n%s' % inputs
        response=json.loads(term_token_counter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['tokens'], \
            'tokens found without term name')
        self.assertFalse(response['success'], \
            'success with missing term name')

    def test_term_token_counter(self):
        print 'testing term_token_counter'
        termtokenfile = self.framework.termtokenfile
        testtokenextractfile = self.framework.testtokenextractfile
        termname = 'locality'
        
        inputs = {}
        inputs['inputfile'] = termtokenfile
        inputs['outputfile'] = testtokenextractfile
        inputs['termname'] = termname

        # Extract distinct values of term
#        print 'inputs:\n%s' % inputs
        response=json.loads(term_token_counter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        tokens = response['tokens']
        s = 'no tokens for term %s from file %s' % \
            (termname, termtokenfile)
        self.assertIsNotNone(tokens, s)
        
        tokenlist = tokens['tokenlist']
        s = 'no tokenlist for term %s from file %s' % \
            (termname, termtokenfile)
        self.assertIsNotNone(tokens, s)

        parametercount = len(tokens)
        expected = 5
        s = 'parameter count (%s) for response not correct' % parametercount
        self.assertEqual(parametercount, expected, s)

        distincttokencount = 38
        s = 'distincttokencount (%s) not as expected (%s)' % \
            (len(tokens['tokenlist']), distincttokencount)
        self.assertEqual(len(tokens['tokenlist']),distincttokencount,s)

        value = 'of'
        totalcount = 3
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

        value = 'National'
        totalcount = 2
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

        value = 'Ridge'
        totalcount = 1
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

if __name__ == '__main__':
    unittest.main()
