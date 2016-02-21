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
__version__ = "csv_fieldcount_checker_test.py 2016-02-21T16:00-03:00"

# This file contains unit test for the csv_fieldcount_checker function.
#
# Example:
#
# python csv_fieldcount_checker_test.py

from csv_fieldcount_checker import csv_fieldcount_checker
import os
import json
import unittest

class CsvFieldcountCheckerFramework():
    """Test framework for the Darwin Cloud collector."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_fieldcount.csv'
    testfile3 = testdatapath + 'test_bad_fieldcount1.txt'

    # output data files from tests, remove these in dispose()
#    testcollectorfile = testdatapath + 'test_collector_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
#         testcollectorfile = self.testcollectorfile
#         if os.path.isfile(testcollectorfile):
#             os.remove(testcollectorfile)
        return True

class CsvFieldcountCheckerTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = CsvFieldcountCheckerFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile), testfile + ' does not exist')
        testfile = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile), testfile + ' does not exist')
        testfile = self.framework.testfile3
        self.assertTrue(os.path.isfile(testfile), testfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile1 = self.framework.testfile1

        inputs = {}
        response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertEquals(response['firstbadrowindex'], 0, \
            'bad row found without input file')
        self.assertFalse(response['success'], \
            'success without input file')

        inputs['inputfile'] = ''
        response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertEquals(response['firstbadrowindex'], 0, \
            'bad row found with blank input file')
        self.assertTrue(response['success'], \
            'success with blank input file')

    def test_csv_fieldcount_checker(self):
        print 'testing csv_fieldcount_checker'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testfile3 = self.framework.testfile3
        
        inputs = {}
        inputs['inputfile'] = testfile1

        # Check for bad rows
        response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
        s = 'Bad row found for file %s' % (testfile1)
        firstbadrowindex = response['firstbadrowindex']
        self.assertEqual(firstbadrowindex, 0, s)
#        self.assertIsNone(response, s)
        
        inputs['inputfile'] = testfile2
        response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
        s = 'No bad row found for file %s' % (testfile2)
        self.assertIsNotNone(response, s)
        firstbadrowindex = response['firstbadrowindex']
#        print 'values:\n%s\nexpected:\n%s' % (values,expected)
        s = 'File %s, first bad row: %s\nrow:\n%s' \
            % (testfile2, response['firstbadrowindex'], response['row'])
        self.assertEqual(firstbadrowindex, 3, s)

        inputs['inputfile'] = testfile3
        response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
        s = 'No bad row found for file %s' % (testfile3)
        self.assertIsNotNone(response, s)
        firstbadrowindex = response['firstbadrowindex']
#        print 'values:\n%s\nexpected:\n%s' % (values,expected)
        s = 'File %s, first bad row: %s\nrow:\n%s' \
            % (testfile3, response['firstbadrowindex'], response['row'])
        self.assertEqual(firstbadrowindex, 3, s)

if __name__ == '__main__':
    unittest.main()
