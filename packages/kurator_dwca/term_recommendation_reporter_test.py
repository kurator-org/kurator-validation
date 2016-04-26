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
__version__ = "term_recommendation_reporter_test.py 2016-04-05T11:43-03:00"

# This file contains unit tests for the term_recommendation_reporter function.
#
# Example:
#
# python term_recommendation_reporter_test.py

from term_recommendation_reporter import term_recommendation_reporter
import os
import json
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

        inputs = {}
        response=json.loads(term_recommendation_reporter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['newvalues'], \
            'recommendations reported without input file')
        self.assertFalse(response['success'], \
            'success without input file')

        inputs['inputfile'] = testfile
#        print 'inputs:\n%s' % inputs
        response=json.loads(term_recommendation_reporter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['newvalues'], \
            'recommendations reported without vocab file')
        self.assertFalse(response['success'], \
            'success with missing term name')

        inputs['vocabfile'] = monthvocabfile
#        print 'inputs:\n%s' % inputs
        response=json.loads(term_recommendation_reporter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertIsNone(response['newvalues'], \
            'recommendations reported without term name')
        self.assertFalse(response['success'], \
            'success with missing term name')

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
        response=json.loads(term_recommendation_reporter(json.dumps(inputs)))
#        print 'response:\n%s' % response
        success = response['success']
        s = 'term recommendation failed: %s' % response['message']
        self.assertTrue(success, s)

        newvalues = response['newvalues']
        expected = ['grr']
        s = 'newvalues:\n%s\nnot as expected:\n%s' \
            % (newvalues, expected)
        self.assertEqual(newvalues, expected, s)

if __name__ == '__main__':
    unittest.main()
