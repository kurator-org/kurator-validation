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
__version__ = "composite_header_constructor_test.py 2016-05-27T21:59-03:00"

# This file contains unit test for the composite_header_constructor function.
#
# Example:
#
# python composite_header_constructor_test.py

from composite_header_constructor import composite_header_constructor
from dwca_utils import read_header
from dwca_utils import write_header
import os
import unittest

class CompositeHeaderConstructorFramework():
    """Test framework for the composite header constructor."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'
    workspace = './workspace/'
    
    # input data files to tests, don't remove these
    tsvtest1 = testdatapath + 'test_tsv_1.txt'
    tsvtest2 = testdatapath + 'test_tsv_2.txt'
    csvtest1 = testdatapath + 'test_csv_1.csv'
    csvtest2 = testdatapath + 'test_csv_2.csv'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_composed_header.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        removeme = self.workspace + self.outputfile
        if os.path.isfile(removeme):
            os.remove(removeme)
        return True

class CompositeHeaderConstructorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = CompositeHeaderConstructorFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        tsvfile1 = self.framework.tsvtest1
        tsvfile2 = self.framework.tsvtest2
        csvfile1 = self.framework.csvtest1
        csvfile2 = self.framework.csvtest2
        self.assertTrue(os.path.isfile(tsvfile1), tsvfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(tsvfile2), tsvfile2 + ' does not exist')
        self.assertTrue(os.path.isfile(csvfile1), csvfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(csvfile2), csvfile2 + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        tsvfile1 = self.framework.tsvtest1
        tsvfile2 = self.framework.tsvtest2
        outputfile = self.framework.outputfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=composite_header_constructor(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs['inputfile1'] = tsvfile1
        response=composite_header_constructor(inputs)
#        print 'response2:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with no input files
        inputs = {}
        inputs['outputfile'] = outputfile
        response=composite_header_constructor(inputs)
#        print 'response3:\n%s' % response
        s = 'success without any input files'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['inputfile2'] = tsvfile2
        response=composite_header_constructor(inputs)
#        print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)

        inputs = {}
        inputs['outputfile'] = outputfile
        inputs['inputfile1'] = tsvfile1
        response=composite_header_constructor(inputs)
#        print 'response5:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_source_headers_correct(self):
        print 'testing source_headers_correct'
        tsvfile1 = self.framework.tsvtest1
        tsvfile2 = self.framework.tsvtest2
        csvfile1 = self.framework.csvtest1
        csvfile2 = self.framework.csvtest2

        header = read_header(tsvfile1)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:%s\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

        header = read_header(tsvfile2)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

        header = read_header(csvfile2)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:%s\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

        header = read_header(csvfile1)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:%s\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_compose(self):
        print 'testing compose'
        workspace = self.framework.workspace
        tsvfile1 = self.framework.tsvtest1
        tsvfile2 = self.framework.tsvtest2
        csvfile1 = self.framework.csvtest1
        csvfile2 = self.framework.csvtest2
        outputfile = self.framework.outputfile

        inputs = {}
        inputs['inputfile1'] = tsvfile1
        inputs['inputfile2'] = tsvfile2
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace

        response=composite_header_constructor(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'composite header not created'
        self.assertTrue(success, s)
        s = 'incorrect number of columns in composite'
        self.assertEqual(len(response['compositeheader']), 6, s)
        expected = ['decimalLatitude', 'decimalLongitude', 'locality', \
            'materialSampleID', 'phylum', 'principalInvestigator']
        s = 'composite header:\n%s\nnot as expected:\n%s' % \
            (response['compositeheader'], expected)
        self.assertEqual(response['compositeheader'], expected, s)

if __name__ == '__main__':
    print '=== composite_header_constructor_test.py ==='
    unittest.main()
