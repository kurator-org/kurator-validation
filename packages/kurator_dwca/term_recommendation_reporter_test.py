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
__version__ = "term_recommendation_reporter_test.py 2016-05-11T22:48-03:00"

# This file contains unit tests for the term_recommendation_reporter function.
#
# Example:
#
# python term_recommendation_reporter_test.py

from term_recommendation_reporter import term_recommendation_reporter
import os
import unittest

class TermRecommendationReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
#    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile1 = testdatapath + 'test_month_report.txt'
    monthvocabfile = testdatapath + 'test_vocab_month.txt'

    # output data files from tests, remove these in dispose()
    testreportfile = testdatapath + 'test_term_recommendation_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testreportfile
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        return True

class TermRecommendationReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TermRecommendationReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile1 = self.framework.testfile1
        monthvocabfile = self.framework.monthvocabfile
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(monthvocabfile), monthvocabfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile = self.framework.testfile1
        monthvocabfile = self.framework.monthvocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=term_recommendation_reporter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['vocabfile'] = monthvocabfile
        inputs['termname'] = 'month'
        response=term_recommendation_reporter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termname'] = 'month'
        response=term_recommendation_reporter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['vocabfile'] = monthvocabfile
        response=term_recommendation_reporter(inputs)
#        print 'response4:\n%s' % response
        s = 'success without termname'
        self.assertFalse(response['success'], s)

    def test_term_recommendation_reporter(self):
        print 'testing term_recommendation_reporter'
        testfile = self.framework.testfile1
        testreportfile = self.framework.testreportfile
        monthvocabfile = self.framework.monthvocabfile
        termname = 'verbatim'
        
        inputs = {}
        inputs['inputfile'] = testfile
        inputs['termname'] = termname
        inputs['outputfile'] = testreportfile
        inputs['vocabfile'] = monthvocabfile

        # Create the report
#        print 'inputs:\n%s' % inputs
        response=term_recommendation_reporter(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'term recommendation failed: %s' % response['message']
        self.assertTrue(success, s)

if __name__ == '__main__':
    print '=== term_recommendation_reporter_test.py ==='
    unittest.main()
