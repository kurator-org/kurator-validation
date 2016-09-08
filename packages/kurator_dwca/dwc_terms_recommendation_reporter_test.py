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
__version__ = "dwc_terms_recommendation_reporter_test.py 2016-09-06T22:43+02:00"

# This file contains unit tests for the dwc_terms_recommendation_reporter function.
#
# Example:
#
# python dwc_terms_recommendation_reporter_test.py

from dwc_terms_recommendation_reporter import dwc_terms_recommendation_reporter
from dwca_terms import controlledtermlist
import os
import unittest

class DwcTermsRecommendationReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'
    vocabdir = './data/vocabularies/'

    # input data files to tests, don't remove these
    testinput = testdatapath + 'test_occurrence_controlled_vocabs.csv'

    # output data files from tests, remove these in dispose()
#    testreportfile = testdatapath + 'test_term_recommendation_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
#         testreportfile = self.testreportfile
#         if os.path.isfile(testreportfile):
#             os.remove(testreportfile)
        return True

class DwcTermsRecommendationReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DwcTermsRecommendationReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

#     def test_source_files_exist(self):
#         print 'testing source_files_exist'
#         testinput = self.framework.testinput
#         self.assertTrue(os.path.isfile(testinput), testinput + ' does not exist')
#         
#         vocabdir = self.framework.vocabdir
#         for termname in controlledtermlist:
#             vocabfile = vocabdir + termname + '.txt'
#             self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

#     def test_missing_parameters(self):
#         print 'testing missing_parameters'
#         testinput = self.framework.testinput
#         vocabdir = self.framework.vocabdir
# 
#         # Test with missing required inputs
#         # Test with no inputs
#         inputs = {}
#         response=dwc_terms_recommendation_reporter(inputs)
#        # print 'response1:\n%s' % response
#         s = 'success without any required inputs'
#         self.assertFalse(response['success'], s)
# 
#         # Test with missing inputfile
#         inputs['vocabdir'] = vocabdir
#         response=dwc_terms_recommendation_reporter(inputs)
#         # print 'response2:\n%s' % response
#         s = 'success without inputfile'
#         self.assertFalse(response['success'], s)
# 
#         # Test with missing vocabdir
#         inputs = {}
#         inputs['inputfile'] = testinput
#         response=dwc_terms_recommendation_reporter(inputs)
#         # print 'response3:\n%s' % response
#         s = 'success without vocabdir'
#         self.assertFalse(response['success'], s)
# 
#         # Test with missing optional inputs
#         inputs['vocabdir'] = vocabdir
#         response=dwc_terms_recommendation_reporter(inputs)
#         s = 'no output files produced with required inputs'
#         self.assertTrue(response['success'], s)
#         # Remove the files created by this test, as the Framework does not know about them
#         artifacts = response['artifacts']
#         for key, value in artifacts.iteritems():
#             if os.path.isfile(value):
#                 os.remove(value)

    def test_dwc_terms_recommendation_reporter(self):
        print 'testing dwc_terms_recommendation_reporter'
        testdatapath = self.framework.testdatapath
        testinput = self.framework.testinput
        vocabdir = self.framework.vocabdir
        prefix = 'testterms'
        
        inputs = {}
        inputs['inputfile'] = testinput
        inputs['vocabdir'] = vocabdir
        inputs['workspace'] = testdatapath
        inputs['prefix'] = prefix

        # Create the reports
#        print 'inputs:\n%s' % inputs
        response=dwc_terms_recommendation_reporter(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'term recommendation failed: %s' % response['message']
        self.assertTrue(success, s)

        # Check that the reports are correct
        guid = response['guid']
        for termname in controlledtermlist:
            if termname != 'day':
                checkfile = testdatapath + prefix + '_' + termname
                checkfile += '_standardization_report_' + guid + '.csv'
                success = os.path.isfile(checkfile)
                s = 'Report not created for "%s"' % termname
                self.assertTrue(success, s)

        # Remove the files created by this test, as the Framework does not know about them
        artifacts = response['artifacts']

        for key, value in artifacts.iteritems():
            if os.path.isfile(value):
                os.remove(value)

if __name__ == '__main__':
    print '=== dwc_terms_recommendation_reporter_test.py ==='
    unittest.main()
