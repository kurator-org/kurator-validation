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
__version__ = "utf8_test.py 2016-10-21T15:05+02:00"

# This file contains unit test for the UniversalDetector class.
#
# Example:
#
# python utf8_test.py

#from kurator_dwca.utf8_encoder import utf8_encoder
#from kurator_dwca.dwca_utils import csv_file_encoding
from chardet.universaldetector import UniversalDetector
import glob
import os
import unittest

class UTF8EncoderFramework():
    """Test framework for UTF8 Encoder."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_records_utf8_lf.csv'
    testfile2 = testdatapath + 'test_thirty_records_latin_1_crlf.csv'
    testfile3 = testdatapath + 'test_geography_utf8.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_utf8encoded_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        return True

class UTF8EncoderTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = UTF8EncoderFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile1 = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        testfile2 = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile2), testfile2 + ' does not exist')
        testfile3 = self.framework.testfile3
        self.assertTrue(os.path.isfile(testfile3), testfile3 + ' does not exist')

    def test_chardet(self):
        print 'testing chardet'
        testfile3 = self.framework.testfile3
        i = 0

        detector = UniversalDetector()

        for filename in glob.glob('./data/tests/test_*'):
        #for filename in glob.glob('./data/vocabularies/*.txt'):
        #for filename in glob.glob('./data/tests/test_geography*'):
            print filename.ljust(60),
            detector.reset()
            i = 0
            l = 0
            for line in file(filename, 'rb'):
                if detector.done:
                    pass
                else:
                    detector.feed(line)
                    l += 1
                i += 1
            detector.close()
            print '%s after %s lines of %s total' % (detector.result, l, i)
            encoding = detector.result['encoding']

if __name__ == '__main__':
    print '=== utf8_test.py ==='
    unittest.main()
