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
__version__ = "darwin_cloud_collector_test.py 2016-02-08T11:15-03:00"

# This file contains unit test for the darwin_cloud_collector function.
#
# Example:
#
# python darwin_cloud_collector_test.py

from darwin_cloud_collector import darwin_cloud_collector
from dwca_utils import read_header
from dwca_vocab_utils import distinct_term_values_from_file
import os
import json
import unittest

class DarwinCloudCollectorFramework():
    """Test framework for the Darwin Cloud collector."""
    # location for the test inputs and outputs
    testdatapath = '../../data/tests/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_specimen_records.csv'
    testfile2 = testdatapath + 'test_three_specimen_records.txt'

    # output data files from tests, remove these in dispose()
    testcollectorfile = testdatapath + 'test_collector_file.csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testcollectorfile = self.testcollectorfile
        if os.path.isfile(testcollectorfile):
            os.remove(testcollectorfile)
        return True

class DarwinCloudCollectorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DarwinCloudCollectorFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        testfile1 = self.framework.testfile1
        self.assertTrue(os.path.isfile(testfile1), testfile1 + ' does not exist')
        testfile2 = self.framework.testfile2
        self.assertTrue(os.path.isfile(testfile2), testfile2 + ' does not exist')

    def test_headers(self):
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

    def test_darwin_cloud_collector(self):
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        outputfile = self.framework.testcollectorfile
        
        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['outputfile'] = outputfile

        # Collect terms
        response=json.loads(darwin_cloud_collector(json.dumps(inputs)))
        values = response['addedvalues']
        expected = ['CollectionCode','DatasetName','Id','InstitutionCode']
#        print 'values:\n%s expected: %s' % (values,expected)
        s = 'new Darwin Cloud terms %s not extracted correctly from %s' \
            % (values, testfile1)
        self.assertEqual(values, expected, s)

        inputs['inputfile'] = testfile2

        # Collect terms
        response=json.loads(darwin_cloud_collector(json.dumps(inputs)))
        values = response['addedvalues']
        expected = ['BCID','basisOfIdentification','dayCollected','dayIdentified', 
        'extractionID','fundingSource','geneticTissueType','length','microHabitat',
        'monthCollected','monthIdentified','permitInformation','plateID','preservative',
        'previousTissueID','principalInvestigator','sampleOwnerInstitutionCode','species',
        'subSpecies','substratum','tissueStorageID','weight','wellID','wormsID',
        'yearCollected','yearIdentified']
#        print 'values:\n%s\nexpected:\n%s' % (values,expected)
        s = 'new Darwin Cloud terms %s not extracted correctly from %s' \
            % (values, testfile2)
        self.assertEqual(values, expected, s)

if __name__ == '__main__':
    unittest.main()
