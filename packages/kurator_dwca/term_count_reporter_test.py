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
__version__ = "term_count_reporter_test.py 2016-04-26T15:01-03:00"

# This file contains unit tests for the term_count_reporter function.
#
# Example:
#
# python term_count_reporter_test.py

from term_count_reporter import term_count_reporter
import os
#import json
import unittest

class TermCountReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testinputfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testreportfile = 'test_term_report_file.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testdatapath+self.testreportfile
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        return True

class TermCountReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TermCountReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testinputfile = self.framework.testinputfile
        self.assertTrue(os.path.isfile(testinputfile), testinputfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testinputfile = self.framework.testinputfile

        inputs = {}
        response=term_count_reporter(inputs)
#        print 'response:\n%s' % response
        self.assertFalse(response['success'], \
            'success without input file')

        inputs['inputfile'] = testinputfile
#        print 'inputs:\n%s' % inputs
        response=term_count_reporter(inputs)
#        print 'response:\n%s' % response
        self.assertFalse(response['success'], \
            'success with missing term name')

    def test_term_count_reporter(self):
        print 'testing term_count_reporter'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath
        outputfile = '%s/%s' % (workspace.rstrip('/'), testreportfile)
        termname = 'year'
        
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termname'] = termname
        inputs['workspace'] = workspace
        inputs['outputfile'] = testreportfile

        # Create the report
        print 'inputs:\n%s' % inputs
        response=term_count_reporter(inputs)
        print 'response:\n%s' % response
        success = response['success']
        s = 'term report failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        print 'response:\n%s' % response
        self.assertTrue(os.path.isfile(outputfile), outputfile + ' does not exist')

if __name__ == '__main__':
    unittest.main()
