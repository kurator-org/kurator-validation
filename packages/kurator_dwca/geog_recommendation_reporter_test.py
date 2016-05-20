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
__version__ = "geog_recommendation_reporter_test.py 2016-05-20T10:17-03:00"

# This file contains unit tests for the geog_recommendation_reporter function.
#
# Example:
#
# python geog_recommendation_reporter_test.py

from geog_recommendation_reporter import geog_recommendation_reporter
import os
import unittest

class GeogRecommendationReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    inputfile = testdatapath + 'test_eight_specimen_records.csv'
    vocabfile = testdatapath + 'test_geography.txt'

    # output data files from tests, remove these in dispose()
    testreportfile = 'test_geog_recommendation_file.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testdatapath + self.testreportfile
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        return True

class GeogRecommendationReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = GeogRecommendationReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        inputfile = self.framework.inputfile
        vocabfile = self.framework.vocabfile
        self.assertTrue(os.path.isfile(inputfile), inputfile + ' does not exist')
        self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        inputfile = self.framework.inputfile
        vocabfile = self.framework.vocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=geog_recommendation_reporter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs = {}
        inputs['inputfile'] = inputfile
        response=geog_recommendation_reporter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file create by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_geog_recommendation_reporter(self):
        print 'testing geog_recommendation_reporter'
        inputfile = self.framework.inputfile
        testreportfile = self.framework.testreportfile
        vocabfile = self.framework.vocabfile
        workspace = self.framework.testdatapath
        
        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['outputfile'] = testreportfile
        inputs['vocabfile'] = vocabfile
        inputs['workspace'] = workspace

        # Create the report
#        print 'inputs:\n%s' % inputs
        response=geog_recommendation_reporter(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'geog recommendation failed: %s' % response['message']
        self.assertTrue(success, s)

if __name__ == '__main__':
    print '=== geog_recommendation_reporter_test.py ==='
    unittest.main()
