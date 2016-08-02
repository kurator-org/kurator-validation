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
__version__ = "darwinize_header_test.py 2016-08-02T15:53+02:00"

# This file contains unit test for the darwinize_header function.
#
# Example:
#
# python darwinize_header_test.py

from darwinize_header import darwinize_header
from dwca_vocab_utils import terms_not_in_dwc
from dwca_utils import read_header
import os
import unittest

class DarwinizeHeaderFramework():
    """Test framework for Darwinize Header."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'
    dwccloudfile = testdatapath + 'test_dwc_cloud.txt'

    # output data files from tests, remove these in dispose()
    outputfile = 'test_darwinizedheader_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        outputfile = self.testdatapath + self.outputfile
        if os.path.isfile(outputfile):
            os.remove(outputfile)
        return True

class DarwinizeHeaderTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DarwinizeHeaderFramework()

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
        dwccloudfile = self.framework.dwccloudfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=darwinize_header(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['dwccloudfile'] = dwccloudfile
        response=darwinize_header(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing Darwin Cloud Vocab file
        inputs = {}
        inputs['inputfile'] = testfile1
        response=darwinize_header(inputs)
#        print 'response3:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs['dwccloudfile'] = dwccloudfile
        response=darwinize_header(inputs)
#        print 'response4:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        response=darwinize_header(inputs)
#        print 'response5:\n%s' % response
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

    def test_darwinize_header(self):
        print 'testing darwinize_header'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testdatapath = self.framework.testdatapath
        dwccloudfile = self.framework.dwccloudfile
        outputfile = self.framework.outputfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['dwccloudfile'] = dwccloudfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath

        # Darwinize the header
        response=darwinize_header(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        header = read_header(outfilelocation)
#        print 'inputs1:\n%s' % inputs
#        print 'response1:\n%s' % response
        expected = ['catalogNumber', 'recordedBy', 'fieldNumber', 'year', 'month', 'day',
            'decimalLatitude', 'decimalLongitude', 'geodeticDatum', 'country', 
            'stateProvince', 'county', 'locality', 'family', 'scientificName',
            'scientificNameAuthorship', 'reproductiveCondition', 'institutionCode',
            'collectionCode', 'datasetName', 'Id']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, header, expected)
        self.assertEqual(header, expected, s)

        # What is not Darwin Core?
        casesensitive = True
        notdwc = terms_not_in_dwc(header, casesensitive)
        expected = ['Id']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, notdwc, expected)
        self.assertEqual(notdwc, expected, s)
        
        inputs['inputfile'] = testfile2

        # Darwinize the header
        response=darwinize_header(inputs)
        header = read_header(outfilelocation)
#        print 'response2:\n%s' % response
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', 
        'decimalLatitude', 'decimalLongitude', 'coordinateUncertaintyInMeters', 
        'georeferenceProtocol', 'year', 'month', 'day', 'genus', 'specificEpithet', 
        'permitInformation', 'basisOfIdentification', 'taxonID', 'country', 
        'stateProvince', 'island', 'islandGroup', 'sampleOwnerInstitutionCode',
        'fundingSource', 'occurrenceID', 'associatedMedia', 'associatedReferences', 
        'preservative', 'previousIdentifications', 'lifeStage', 'weight', 'length', 
        'sex', 'establishmentMeans', 'associatedSequences', 'occurrenceRemarks', 
        'habitat', 'microHabitat', 'substratum', 'samplingProtocol', 
        'minimumDepthInMeters', 'maximumDepthInMeters', 
        'minimumDistanceAboveSurfaceInMeters', 'maximumDistanceAboveSurfaceInMeters', 
        'associatedTaxa', 'fieldNotes', 'eventRemarks', 'recordedBy', 'identifiedBy', 
        'yearIdentified', 'monthIdentified', 'dayIdentified', 'class', 'order', 'family', 
        'infraspecificEpithet', 'vernacularName', 'taxonRemarks', 'geneticTissueType', 
        'plateID', 'wellID', 'extractionID', 'otherCatalogNumbers', 'tissueStorageID', 
        'BCID', 'unnamedcolumn_1']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile2, header, expected)
        self.assertEqual(header, expected, s)

        # What is not Darwin Core?
        casesensitive = True
        notdwc = terms_not_in_dwc(header, casesensitive)
        expected = [
        'BCID', 'basisOfIdentification', 'dayIdentified', 'extractionID', 'fundingSource',
        'geneticTissueType', 'length', 'microHabitat', 'monthIdentified', 
        'permitInformation', 'plateID', 'preservative', 'principalInvestigator', 
        'sampleOwnerInstitutionCode', 'substratum', 'tissueStorageID', 'unnamedcolumn_1', 
        'weight', 'wellID', 'yearIdentified']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, notdwc, expected)
        self.assertEqual(notdwc, expected, s)

if __name__ == '__main__':
    print '=== darwinize_header_test.py ==='
    unittest.main()
