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
__version__ = "text_file_splitter_test.py 2016-01-22T15:22-03:00"

from text_file_splitter import text_file_splitter
from dwca_utils import split_path
import os
import csv
import glob
import json
import unittest

# This file contains unit test for the text_file_splitter function.
#
# Example:
#
# python text_file_splitter_test.py

class TextFileSplitterFramework():
    """Test framework for the text file splitter."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'
    
    # test file to split
    csvfile = 'test_eight_specimen_records.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testdatapath = self.testdatapath
        path, ext, filename = split_path(testdatapath+self.csvfile)

        # do not remove the source file from the test data path
#        csvfile = self.csvfile        
#        if os.path.isfile(testdatapath + csvfile):
#            os.remove(testdatapath + csvfile)

        files = glob.glob(testdatapath + filename + '*')

        # remove the source file from the list of files to remove from the test data path
        files.remove(testdatapath+self.csvfile)
        
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
        csvfile = self.framework.testdatapath + self.framework.csvfile        
        self.assertTrue(os.path.isfile(csvfile), csvfile + ' does not exist')

    def test_split(self):
        workspace = self.framework.testdatapath
        chunksize = 3
        csvfile = self.framework.testdatapath + self.framework.csvfile        

        inputs = {}
        inputs['inputpath'] = csvfile
        inputs['workspace'] = workspace
        inputs['chunksize'] = chunksize

        print 'inputs:\n%s' % inputs
        print 'json-inputs:\n%s' % json.dumps(inputs)
        # Split text file into chucks
        response=json.loads(text_file_splitter(json.dumps(inputs)))

        path, ext, filename = split_path(workspace+csvfile)
        files = glob.glob(workspace + filename + '*')
        splitfilecount = len(files)-1

        self.assertEqual(response['chunks'], 3, 'incorrect number of chunks')
        self.assertEqual(response['splitrowcount'], 8, 'incorrect number of rows')
        self.assertEqual(splitfilecount, 3, 'incorrect number of chunk files')

if __name__ == '__main__':
    unittest.main()
