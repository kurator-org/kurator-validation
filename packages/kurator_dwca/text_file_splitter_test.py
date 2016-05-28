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
__version__ = "text_file_splitter_test.py 2016-05-27T22:05-03:00"

from text_file_splitter import text_file_splitter
from dwca_utils import split_path
import os
import glob
import unittest

# This file contains unit test for the text_file_splitter function.
#
# Example:
#
# python text_file_splitter_test.py

class TextFileSplitterFramework():
    """Test framework for the text file splitter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'
    
    # test file to split
    inputfile = testdatapath + 'test_eight_specimen_records.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        path, ext, filename = split_path(self.inputfile)

        # do not remove the source file from the test data path
#        csvfile = self.csvfile        
#        if os.path.isfile(testdatapath + csvfile):
#            os.remove(testdatapath + csvfile)

        files = glob.glob(self.testdatapath + filename + '*')

        # remove the source file from the list of files to remove from the test data path
        files.remove(self.inputfile)
        
        # remove the chunked files
        for file in files:
            os.remove(file)
        return True

class TextFileSplitterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TextFileSplitterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_file_exists(self):
        print 'testing source_file_exists'
        inputfile = self.framework.inputfile
        self.assertTrue(os.path.isfile(inputfile), inputfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        workspace = self.framework.testdatapath
        inputfile = self.framework.inputfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=text_file_splitter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['workspace'] = workspace
        response=text_file_splitter(inputs)
#        print 'response2:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
#         if os.path.isfile(response['outputfile']):
#             os.remove(response['outputfile'])

    def test_split(self):
        print 'testing split'
        workspace = self.framework.testdatapath
        chunksize = 3
        inputfile = self.framework.inputfile

        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['workspace'] = workspace
        inputs['chunksize'] = chunksize
#        print 'inputs:\n%s' % inputs

        # Split text file into chucks
        response=text_file_splitter(inputs)
#        print 'response:\n%s' % response

        path, ext, filename = split_path(inputfile)
        files = glob.glob(workspace + filename + '*')
        splitfilecount = len(files)-1

        self.assertEqual(response['chunks'], 3, 'incorrect number of chunks')
        self.assertEqual(response['rowcount'], 8, 'incorrect number of rows')
        self.assertEqual(splitfilecount, 3, 'incorrect number of chunk files')

if __name__ == '__main__':
    print '=== text_file_splitter_test.py ==='
    unittest.main()
