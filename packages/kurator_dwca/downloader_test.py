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
__version__ = "downloader_test.py 2016-04-08T21:09-03:00"

# This file contains unit test for the downloader function.
#
# Example:
#
# python downloader_test.py

from downloader import downloader
import os
import json
import unittest

class DownloaderFramework():
    """Test framework for the downloader."""
    # location for the test inputs and outputs
    workspace = './workspace/'
    outputfile = 'test_ccber_mammals_download.zip'
    testurl = 'http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals'

    # input data files to tests, don't remove these
#    testfile1 = testdatapath + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    testdownloadfile = workspace + outputfile

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testdownloadfile = self.testdownloadfile
        if os.path.isfile(testdownloadfile):
            os.remove(testdownloadfile)
        return True

class DownloaderTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DownloaderFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testurl = self.framework.testurl
        outputfile = self.framework.outputfile
        workspace = self.framework.workspace
        
        inputs = {}
        response=downloader(inputs)
#	        print 'response:\n%s' % response
        self.assertFalse(response['success'], \
            'download returned success without url or outputfile or workspace')

    def test_downloader(self):
        print 'testing downloader'
        testurl = self.framework.testurl
        outputfile = self.framework.outputfile
        workspace = self.framework.workspace
        
        inputs = {}
        inputs['url'] = testurl
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
#        print 'downloader_test.py: inputs:\n%s' % inputs

        # Collect terms
        response=downloader(inputs)
#        print 'downloader_test.py: response:\n%s' % response
        success = response['success']
        s = 'file not downloaded from %s' % testurl 
        self.assertTrue(success, s)

if __name__ == '__main__':
    unittest.main()
