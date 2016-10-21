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
__version__ = "actor_template_test.py 2016-10-20T17:07+02:00"

# This file contains unit test for the dostuffer function.
#
# Example:
#
# python actor_template_test.py

from kurator_dwca.actor_template import dostuffer
import os
import unittest

class DownloaderFramework():
    """Test framework for the dostuffer."""
    # location for the test inputs and outputs
    dataspace = '../data/tests/'
    workspace = './workspace'

    # input data files to tests, don't remove these
    inputfile = dataspace + 'test_eight_specimen_records.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_ccber_mammals_download.zip'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.workspace + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
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
        inputfile = self.framework.inputfile
        outputfile = self.framework.outputfile
        workspace = self.framework.workspace

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=dostuffer(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        response=dostuffer(inputs)
        #print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = inputfile
        response=dostuffer(inputs)
        #print 'response3:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_dostuffer(self):
        print 'testing dostuffer'
        inputfile = self.framework.inputfile
        outputfile = self.framework.outputfile
        workspace = self.framework.workspace

        inputs = {}
        inputs['inputfile'] = inputfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        #print 'actor_template_test.py: inputs:\n%s' % inputs

        # Collect terms
        response=dostuffer(inputs)
        #print 'response:\n%s' % response
        success = response['success']
        s = 'stuff not done with inputfile %s' % inputfile
        s += ' to outputfile %s' % outputfile
        s += ' in workspace %s' % workspace
        self.assertTrue(success, s)

if __name__ == '__main__':
    print '=== actor_template_test.py ==='
    unittest.main()
