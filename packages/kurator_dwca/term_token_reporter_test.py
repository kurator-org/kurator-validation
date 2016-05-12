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
__version__ = "term_token_reporter_test.py 2016-05-11T22:49-03:00"

# This file contains unit test for the term_token_reporter function.
#
# Example:
#
# python term_token_reporter_test.py

from term_token_reporter import term_token_reporter
from dwca_utils import read_header
import os
import unittest

class TermCounterFramework():
    """Test framework for the term counter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    inputfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_token_extract_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
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
        inputfile = self.framework.inputfile
        self.assertTrue(os.path.isfile(inputfile), inputfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        inputfile = self.framework.inputfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=term_token_reporter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['termname'] = 'locality'
        response=term_token_reporter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs = {}
        inputs['inputfile'] = inputfile
        response=term_token_reporter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without term name'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['termname'] = 'locality'
        response=term_token_reporter(inputs)
#        print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file create by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_term_token_reporter(self):
        print 'testing term_token_reporter'
        inputfile = self.framework.inputfile
        outputfile = self.framework.outputfile
        workspace = self.framework.testdatapath
        termname = 'locality'
        
        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        inputs['termname'] = termname

        # Extract tokens from term
#        print 'inputs:\n%s' % inputs
        response=term_token_reporter(inputs)
#        print 'response:\n%s' % response
        tokens = response['tokens']
        s = 'no tokens for term %s from file %s' % \
            (termname, inputfile)
        self.assertIsNotNone(tokens, s)
        
        tokenlist = tokens['tokenlist']
        s = 'no tokenlist for term %s from file %s' % \
            (termname, inputfile)
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
    print '=== term_token_reporter_test.py ==='
    unittest.main()
