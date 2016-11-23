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
__version__ = "darwin_cloud_collector_test.py 2016-10-20T19:36+02:00"

# This file contains unit test for the darwin_cloud_collector function.
#
# Example:
#
# python darwin_cloud_collector_test.py

from kurator_dwca.darwin_cloud_collector import darwin_cloud_collector
from kurator_dwca.dwca_utils import read_header
import os
import unittest

class DarwinCloudCollectorFramework():
    """Test framework for the Darwin Cloud collector."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_collector_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        return True

class DarwinCloudCollectorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DarwinCloudCollectorFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        testfile1 = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        testfile2 = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile2), testfile2 + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile1 = self.framework.testfile1
        outputfile = self.framework.outputfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=darwin_cloud_collector(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        response=darwin_cloud_collector(inputs)
        #print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs = {}
        inputs['inputfile'] = testfile1
        response=darwin_cloud_collector(inputs)
        #print 'response3:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        #print 'inputs:\n%s' % inputs
        response=darwin_cloud_collector(inputs)
        #print 'response4:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_headers(self):
        print 'testing headers'
        testfile = self.framework.testfile1

        header = read_header(testfile)
        expected = ['catalogNumber ','recordedBy','fieldNumber ','year','month','day',
            'decimalLatitude ','decimalLongitude ','geodeticDatum ','country',
            'stateProvince','county','locality','family ','scientificName ',
            'scientificNameAuthorship ','reproductiveCondition ','InstitutionCode ',
            'CollectionCode ','DatasetName ','Id']
        s = 'test file %s header:\n%s does not match expected:\n%s' % (testfile, header, expected)
        self.assertEqual(header, expected)

        testfile = self.framework.testfile2
        header = read_header(testfile)
        expected = ['materialSampleID','principalInvestigator','locality','phylum',
            'decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters',
            'georeferenceProtocol','yearCollected','monthCollected','dayCollected',
            'genus','species','permitInformation','basisOfIdentification','wormsID',
            'country','stateProvince','island','islandGroup','sampleOwnerInstitutionCode',
            'fundingSource','occurrenceID','associatedMedia','associatedReferences',
            'preservative','previousIdentifications','lifeStage','weight','length','sex',
            'establishmentMeans','associatedSequences','occurrenceRemarks','habitat',
            'microHabitat','substratum','samplingProtocol','minimumDepthInMeters',
            'maximumDepthInMeters','minimumDistanceAboveSurfaceInMeters',
            'maximumDistanceAboveSurfaceInMeters','associatedTaxa','fieldNotes',
            'eventRemarks','recordedBy','identifiedBy','yearIdentified','monthIdentified',
            'dayIdentified','class','order','family','subSpecies','vernacularName',
            'taxonRemarks','geneticTissueType','plateID','wellID','extractionID',
            'previousTissueID','tissueStorageID','BCID','']
        s = 'test file %s header:\n%s does not match expected:\n%s' % \
            (testfile, header, expected)
        self.assertEqual(header, expected)

    def test_darwin_cloud_collector(self):
        print 'testing darwin_cloud_collector'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testdatapath = self.framework.testdatapath
        outputfile = self.framework.outputfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath

        # Collect terms
        response=darwin_cloud_collector(inputs)
        #print 'response1:\n%s' % response
        addedvalues = response['addedvalues']
        expected = ['ID']
        #print 'addedvalues:\n%s expected: %s' % (addedvalues,expected)
        s = 'From: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, addedvalues, expected)
        self.assertEqual(addedvalues, expected, s)

        inputs['inputfile'] = testfile2

        # Collect terms
        response=darwin_cloud_collector(inputs)
        #print 'response2:\n%s' % response
        addedvalues = response['addedvalues']
        expected = ['BASISOFIDENTIFICATION', 'BCID', 'DAYCOLLECTED', 'DAYIDENTIFIED', 
            'EXTRACTIONID', 'FUNDINGSOURCE', 'GENETICTISSUETYPE', 'LENGTH', 
            'MICROHABITAT', 'MONTHCOLLECTED', 'MONTHIDENTIFIED', 'PERMITINFORMATION', 
            'PLATEID', 'PRESERVATIVE', 'PREVIOUSTISSUEID', 'PRINCIPALINVESTIGATOR', 
            'SAMPLEOWNERINSTITUTIONCODE', 'SPECIES', 'SUBSPECIES', 'SUBSTRATUM', 
            'TISSUESTORAGEID', 'WEIGHT', 'WELLID', 'WORMSID', 'YEARCOLLECTED', 
            'YEARIDENTIFIED']
        #print 'addedvalues:\n%s\nexpected:\n%s' % (addedvalues,expected)
        s = 'From: %s\nFound:\n%s\nExpected:\n%s' % (testfile2, addedvalues, expected)
        self.assertEqual(addedvalues, expected, s)

if __name__ == '__main__':
    print '=== darwin_cloud_collector_test.py ==='
    unittest.main()
