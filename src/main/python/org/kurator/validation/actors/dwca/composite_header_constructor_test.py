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
__version__ = "composite_header_constructor_test.py 2016-02-12T11:58-03:00"

# This file contains unit test for the composite_header_constructor function.
#
# Example:
#
# python composite_header_constructor_test.py

from composite_header_constructor import composite_header_constructor
from dwca_utils import read_header
from dwca_utils import write_header
import os
import csv
import glob
import json
import unittest

class CompositeHeaderConstructorFramework():
    """Test framework for the composite header constructor."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'
    workspace = './workspace'
    
    # input data files to tests, don't remove these
    tsvtest1 = testdatapath + 'test_tsv_1.txt'
    tsvtest2 = testdatapath + 'test_tsv_2.txt'
    csvtest1 = testdatapath + 'test_csv_1.csv'
    csvtest2 = testdatapath + 'test_csv_2.csv'

    # output data files from tests, remove these in dispose()
    composedheaderfile = 'test_composed_header.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        removeme = self.workspace + '/'+ self.composedheaderfile
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
        composedheaderfile = self.framework.composedheaderfile

        inputs = {}
        inputs['file1'] = tsvfile1
        inputs['file2'] = tsvfile2
        inputs['workspace'] = workspace
        inputs['headerfilename'] = composedheaderfile

        response=json.loads(composite_header_constructor(json.dumps(inputs)))
#        print 'composite header:\n%s\ncompositeheaderoutputfile: %s' % (response['compositeheader'], response['compositeheaderoutputfile'])
        self.assertEqual(len(response['compositeheader']), 6, 'incorrect number of columns in composite')

if __name__ == '__main__':
    unittest.main()
