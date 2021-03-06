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
__version__ = "term_value_count_reporter_test.py 2016-10-21T12:44+02:00"

# This file contains unit tests for the term_value_count_reporter function.
#
# Example:
#
# python term_value_count_reporter_test.py

from kurator_dwca.term_value_count_reporter import term_value_count_reporter
import os
import unittest

class TermValueCountReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'

    # input data files to tests, don't remove these
    testinputfile = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testreportfile = 'test_term_count_report_file.csv'
    testreportfile2 = 'test_term_count_report_file2.csv'
    testreportfile3 = 'test_term_count_report_file3.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testreportfile = self.testdatapath+self.testreportfile
        testreportfile2 = self.testdatapath+self.testreportfile2
        testreportfile3 = self.testdatapath+self.testreportfile3
        if os.path.isfile(testreportfile):
            os.remove(testreportfile)
        if os.path.isfile(testreportfile2):
            os.remove(testreportfile2)
        if os.path.isfile(testreportfile3):
            os.remove(testreportfile3)
        return True

class TermValueCountReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TermValueCountReporterFramework()

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
        testreportfile = self.framework.testreportfile
        workspace = self.framework.testdatapath

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=term_value_count_reporter(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing termname
        inputs['inputfile'] = testinputfile
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=term_value_count_reporter(inputs)
        #print 'response2:\n%s' % response
        s = 'success without termname'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['termlist'] = ['year']
        inputs['outputfile'] = testreportfile
        inputs['workspace'] = workspace
        response=term_value_count_reporter(inputs)
        #print 'response3:\n%s' % response
        s = 'success without input file'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termlist'] = ['year']
        response=term_value_count_reporter(inputs)
        #print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_term_value_count_reporter(self):
        print 'testing term_value_count_reporter'
        testinputfile = self.framework.testinputfile
        testreportfile = self.framework.testreportfile
        testreportfile2 = self.framework.testreportfile2
        testreportfile3 = self.framework.testreportfile3
        workspace = self.framework.testdatapath
        outputfile = '%s/%s' % (workspace.rstrip('/'), testreportfile)
        termlist = ['year']
        
        inputs = {}
        inputs['inputfile'] = testinputfile
        inputs['termlist'] = termlist
        inputs['workspace'] = workspace
        inputs['outputfile'] = testreportfile

        # Create the report
        #print 'inputs:\n%s' % inputs
        response=term_value_count_reporter(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'term report failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        #print 'response:\n%s' % response
        self.assertTrue(os.path.isfile(outputfile), outputfile + ' does not exist')

        termlist = ['country', 'stateprovince']
        inputs['termlist'] = termlist
        inputs['outputfile'] = testreportfile2
        # Create the report
        #print 'inputs:\n%s' % inputs
        response=term_value_count_reporter(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'term report failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        #print 'response:\n%s' % response
        self.assertTrue(os.path.isfile(outputfile), outputfile + ' does not exist')

        termlist = ['continent', 'country', 'countrycode', 'stateprovince', 'county', 
                 'municipality', 'waterbody', 'islandgroup', 'island']
        inputs['termlist'] = termlist
        inputs['outputfile'] = testreportfile3
        # Create the report
        #print 'inputs:\n%s' % inputs
        response=term_value_count_reporter(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'term report failed: %s' % response['message']
        self.assertTrue(success, s)

        outputfile = response['outputfile']
        #print 'response:\n%s' % response
        self.assertTrue(os.path.isfile(outputfile), outputfile + ' does not exist')

if __name__ == '__main__':
    print '=== term_value_count_reporter_test.py ==='
    unittest.main()
