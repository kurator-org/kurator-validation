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
__version__ = "darwinize_header_test.py 2017-07-19T11:03-07:00"

# This file contains unit test for the darwinize_header function.
#
# Example:
#
# python darwinize_header_test.py

from kurator_dwca.darwinize_header import darwinize_header
from kurator_dwca.dwca_vocab_utils import terms_not_in_dwc
from kurator_dwca.dwca_utils import read_header
from kurator_dwca.dwca_utils import csv_file_dialect
from kurator_dwca.dwca_utils import csv_dialect
from kurator_dwca.dwca_utils import tsv_dialect
from kurator_dwca.dwca_utils import dialects_equal
import os
import unittest

class DarwinizeHeaderFramework():
    """Test framework for Darwinize Header."""
    # location for the test inputs and outputs
    testdatapath = '../data/tests/'
    vocabpath = '../data/vocabularies/'

    # input data files to tests, don't remove these
    testfile1 = testdatapath + 'test_eight_records_utf8_lf.csv'
    testfile2 = testdatapath + 'test_three_records_utf8_unix_lf.txt'
    testfile3 = testdatapath + 'test_symbiota_download.csv'
    dwccloudfile = vocabpath + 'darwin_cloud.txt'

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
        testfile3 = self.framework.testfile3
        self.assertTrue(os.path.isfile(testfile3), testfile3 + ' does not exist')
        dwccloudfile = self.framework.dwccloudfile
        self.assertTrue(os.path.isfile(dwccloudfile), dwccloudfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        testfile1 = self.framework.testfile1
        outputfile = self.framework.outputfile
        dwccloudfile = self.framework.dwccloudfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=darwinize_header(inputs)
        #print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['dwccloudfile'] = dwccloudfile
        response=darwinize_header(inputs)
        #print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing Darwin Cloud Vocab file
        inputs = {}
        inputs['inputfile'] = testfile1
        response=darwinize_header(inputs)
        #print 'response3:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing outputfile
        inputs['dwccloudfile'] = dwccloudfile
        response=darwinize_header(inputs)
        #print 'response4:\n%s' % response
        s = 'success without outputfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs['outputfile'] = outputfile
        response=darwinize_header(inputs)
       #print 'response5:\n%s' % response
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

        testfile = self.framework.testfile3

        header = read_header(testfile)
        expected = ['id', 'institutionCode', 'collectionCode', 'basisOfRecord', 
            'occurrenceID', 'catalogNumber', 'otherCatalogNumbers', 'kingdom', 'phylum',
            'class', 'order', 'family', 'scientificName', 'scientificNameAuthorship',
            'genus', 'specificEpithet', 'taxonRank', 'infraspecificEpithet',
            'identifiedBy', 'dateIdentified', 'identificationReferences', 
            'identificationRemarks', 'taxonRemarks', 'identificationQualifier',
            'typeStatus', 'recordedBy', 'recordedByID', 'associatedCollectors', 
            'recordNumber', 'eventDate', 'year', 'month', 'day', 'startDayOfYear',
            'endDayOfYear', 'verbatimEventDate', 'occurrenceRemarks', 'habitat', 
            'substrate', 'verbatimAttributes', 'fieldNumber', 'informationWithheld',
            'dataGeneralizations', 'dynamicProperties', 'associatedTaxa', 
            'reproductiveCondition', 'establishmentMeans', 'cultivationStatus', 
            'lifeStage', 'sex', 'individualCount', 'samplingProtocol', 'samplingEffort',
            'preparations', 'country', 'stateProvince', 'county', 'municipality', 
            'locality', 'locationRemarks', 'localitySecurity', 'localitySecurityReason',
            'decimalLatitude', 'decimalLongitude', 'geodeticDatum', 
            'coordinateUncertaintyInMeters', 'verbatimCoordinates', 'georeferencedBy',
            'georeferenceProtocol', 'georeferenceSources', 
            'georeferenceVerificationStatus', 'georeferenceRemarks', 
            'minimumElevationInMeters', 'maximumElevationInMeters', 
            'minimumDepthInMeters', 'maximumDepthInMeters', 'verbatimDepth', 
            'verbatimElevation', 'disposition', 'language', 'recordEnteredBy', 
            'modified', 'sourcePrimaryKey', 'collId', 'recordId', 'references']
        s = 'test file %s header:\n%s does not match expected:\n%s' % (testfile, header, expected)
        self.assertEqual(header, expected)

    def test_darwinize_header(self):
        print 'testing darwinize_header'
        testfile1 = self.framework.testfile1
        testfile2 = self.framework.testfile2
        testfile3 = self.framework.testfile3
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
        #print 'inputs1:\n%s' % inputs
        #print 'response1:\n%s' % response
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
        #print 'response2:\n%s' % response
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
        'BCID', 'UNNAMED_COLUMN_1']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile2, header, expected)
        self.assertEqual(header, expected, s)

        # What is not Darwin Core?
        casesensitive = True
        notdwc = terms_not_in_dwc(header, casesensitive)
        expected = [
        'BCID', 'UNNAMED_COLUMN_1', 'basisOfIdentification', 'dayIdentified', 
        'extractionID', 'fundingSource', 'geneticTissueType', 'length', 'microHabitat', 
        'monthIdentified', 'permitInformation', 'plateID', 'preservative', 
        'principalInvestigator', 'sampleOwnerInstitutionCode', 'substratum', 
        'tissueStorageID', 'weight', 'wellID', 'yearIdentified']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, notdwc, expected)
        self.assertEqual(notdwc, expected, s)

        inputs['inputfile'] = testfile3

        # Darwinize the header
        response=darwinize_header(inputs)
        header = read_header(outfilelocation)
        #print 'response2:\n%s' % response
        expected = ['id', 'institutionCode', 'collectionCode', 'basisOfRecord', 
            'occurrenceID', 'catalogNumber', 'otherCatalogNumbers', 'kingdom', 'phylum',
            'class', 'order', 'family', 'scientificName', 'scientificNameAuthorship',
            'genus', 'specificEpithet', 'taxonRank', 'infraspecificEpithet',
            'identifiedBy', 'dateIdentified', 'identificationReferences', 
            'identificationRemarks', 'taxonRemarks', 'identificationQualifier',
            'typeStatus', 'recordedBy', 'recordedByID', 'associatedCollectors', 
            'recordNumber', 'eventDate', 'year', 'month', 'day', 'startDayOfYear',
            'endDayOfYear', 'verbatimEventDate', 'occurrenceRemarks', 'habitat', 
            'substrate', 'verbatimAttributes', 'fieldNumber', 'informationWithheld',
            'dataGeneralizations', 'dynamicProperties', 'associatedTaxa', 
            'reproductiveCondition', 'establishmentMeans', 'cultivationStatus', 
            'lifeStage', 'sex', 'individualCount', 'samplingProtocol', 'samplingEffort',
            'preparations', 'country', 'stateProvince', 'county', 'municipality', 
            'locality', 'locationRemarks', 'localitySecurity', 'localitySecurityReason',
            'decimalLatitude', 'decimalLongitude', 'geodeticDatum', 
            'coordinateUncertaintyInMeters', 'verbatimCoordinates', 'georeferencedBy',
            'georeferenceProtocol', 'georeferenceSources', 
            'georeferenceVerificationStatus', 'georeferenceRemarks', 
            'minimumElevationInMeters', 'maximumElevationInMeters', 
            'minimumDepthInMeters', 'maximumDepthInMeters', 'verbatimDepth', 
            'verbatimElevation', 'disposition', 'language', 'recordEnteredBy', 
            'modified', 'sourcePrimaryKey', 'collId', 'recordId', 'references']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile3, header, expected)
        self.maxDiff = None
        self.assertEqual(header, expected, s)

        # What is not Darwin Core?
        casesensitive = True
        notdwc = terms_not_in_dwc(header, casesensitive)
        expected = [
        'associatedCollectors', 'collId', 'cultivationStatus', 'id', 'localitySecurity', 
        'localitySecurityReason', 'recordEnteredBy', 'recordId', 'recordedByID', 
        'sourcePrimaryKey', 'substrate', 'verbatimAttributes']
        s = 'From input: %s\nFound:\n%s\nExpected:\n%s' % (testfile1, notdwc, expected)
        self.assertEqual(notdwc, expected, s)

    def test_format(self):
        print 'testing darwinize_header'
        testfile1 = self.framework.testfile1
        testdatapath = self.framework.testdatapath
        dwccloudfile = self.framework.dwccloudfile
        outputfile = self.framework.outputfile

        inputs = {}
        inputs['inputfile'] = testfile1
        inputs['dwccloudfile'] = dwccloudfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = testdatapath
        inputs['format'] = 'csv'

        # Darwinize the header
        response=darwinize_header(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        dialect = csv_file_dialect(outfilelocation)
        self.assertTrue(dialects_equal(dialect, csv_dialect()), outfilelocation + ' dialect not csv')
        
        inputs['format'] = 'txt'

        # Darwinize the header
        response=darwinize_header(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        dialect = csv_file_dialect(outfilelocation)
        self.assertTrue(dialects_equal(dialect, tsv_dialect()), outfilelocation + ' dialect not tsv')
        
        inputs['format'] = None

        # Darwinize the header
        response=darwinize_header(inputs)
        outfilelocation = '%s/%s' % (testdatapath, outputfile)
        inputdialect = csv_file_dialect(outfilelocation)
        outputdialect = csv_file_dialect(testfile1)
        self.assertTrue(dialects_equal(inputdialect, outputdialect), outfilelocation + ' dialect not same as dialect of ' + testfile1)
        

if __name__ == '__main__':
    print '=== darwinize_header_test.py ==='
    unittest.main()
