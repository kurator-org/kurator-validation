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
__version__ = "dwc_geog_collector_test.py 2016-08-23T10:13+02:00"

# This file contains unit test for the dwc_geog_collector function.
#
# Example:
#
# python dwc_geog_collector_test.py

from dwc_geog_collector import dwc_geog_collector
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_utils import read_header
from dwca_terms import geogkeytermlist
import os
import unittest

class DwCGeogCollectorFramework():
    """Test framework for the Darwin Core Geography collector."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
    vocabfile = testdatapath + 'test_geog_collector_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        vocabfile = self.vocabfile
        if os.path.isfile(vocabfile):
            os.remove(vocabfile)
        return True

class DwCGeogCollectorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DwCGeogCollectorFramework()

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
        vocabfile = self.framework.vocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=dwc_geog_collector(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs['inputfile'] = testfile1
        response=dwc_geog_collector(inputs)
#        print 'response2:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs = {}
        inputs['vocabfile'] = vocabfile
        response=dwc_geog_collector(inputs)
#        print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

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
        s = 'test file %s header:\n%s does not match expected:\n%s' % (testfile, header, expected)
        self.assertEqual(header, expected)

    def test_dwc_geog_collector(self):
        print 'testing dwc_geog_collector'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        vocabfile = self.framework.vocabfile

        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['vocabfile'] = vocabfile

        # Collect terms
        response=dwc_geog_collector(inputs)
        addedvalues = response['addedvalues']
        expected = [
            '|United States||California|Kern||||', 
            '|United States||California|San Bernardino||||',
            '|United States||California|||||',
            '|United States||Colorado|||||',
            '|United States||Hawaii|Honolulu||||',
            '|United States||Washington|Chelan||||'
        ]
#        print 'addedvalues:\n%s\nexpected: %s' % (addedvalues,expected)
#        print 'inputs: %s\nresponse1:\n%s' % (inputs, response)
        s = 'New Darwin Core geography terms %s not added correctly from %s' \
            % (addedvalues, testfile1)
        self.assertEqual(addedvalues, expected, s)

        inputs['inputfile'] = testfile2

        # Collect terms
        response=dwc_geog_collector(inputs)
        addedvalues = response['addedvalues']
        expected = [
            '|Mozambique||Maputo|||||Inhaca',
            '|South Africa||Kwa-Zulu Natal|||||'
        ]
#        print 'addedvalues:\n%s\nexpected:\n%s' % (addedvalues,expected)
#        print 'response2:\n%s' % response
        s = 'New Darwin Core geography terms %s not added correctly from input file %s' \
            % (addedvalues, testfile2)
        self.assertEqual(addedvalues, expected, s)
        
        dialect = vocab_dialect()
#        geogkey = compose_key_from_list(geogkeytermlist)
#        print 'geogkey: %s' % geogkey
        existinggeogs = distinct_term_values_from_file(vocabfile, 'geogkey', separator='', dialect=dialect)
        expected = [
            '|Mozambique||Maputo|||||Inhaca',
            '|South Africa||Kwa-Zulu Natal|||||',
            '|United States||California|Kern||||', 
            '|United States||California|San Bernardino||||',
            '|United States||California|||||',
            '|United States||Colorado|||||',
            '|United States||Hawaii|Honolulu||||',
            '|United States||Washington|Chelan||||'
        ]
        s = 'Resulting Darwin Core geography file %s ' % vocabfile
        s += 'not correct from input files %s and %s\n' % (testfile1, testfile2)
        s += 'Found:\n%s\nExpected:\n%s' % (existinggeogs, expected)
        self.assertEqual(existinggeogs, expected, s)

if __name__ == '__main__':
    print '=== dwc_geog_collector_test.py ==='
    unittest.main()
