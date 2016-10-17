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
__version__ = "dwca_core_to_tsv_test.py 2016-10-17T14:47+02:00"

# This file contains unit test for the dwca_core_to_tsv function.
#
# Example:
#
# python dwca_core_to_tsv_test.py

from dwca_core_to_tsv import dwca_core_to_tsv
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import tsv_dialect
import os
import unittest

class DwcaCoreToTsvFramework():
    """Test framework for the Darwin Core archive to TSV converter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'
    archivetype = 'standard'

    # input data files to test, don't remove these
    dwca = testdatapath + 'dwca-uwymv_herp.zip'

    # output data files from tests, remove these in dispose()
#    outputfile = testdatapath + 'test_tsv_from_dwca.txt'
    outputfile = 'test_tsv_from_dwca.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        removeme = self.testdatapath + self.outputfile
        #print 'removeme: %s' % removeme
        if os.path.isfile(removeme):
            os.remove(removeme)
        return True

class DwcaCoreToTsvTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = DwcaCoreToTsvFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        dwca = self.framework.dwca
        self.assertTrue(os.path.isfile(dwca), dwca + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        dwca = self.framework.dwca
        outputfile = self.framework.outputfile
        workspace = self.framework.testdatapath

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=dwca_core_to_tsv(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        response=dwca_core_to_tsv(inputs)
#        print 'response2:\n%s' % response
        s = 'success without dwca file'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs
        inputs = {}
        inputs['inputfile'] = dwca
        response=dwca_core_to_tsv(inputs)
#        print 'response3:\n%s' % response
        s = 'no output file produced with required inputs'
        self.assertTrue(response['success'], s)
        # Remove the file created by this test, as the Framework does not know about it
        if os.path.isfile(response['outputfile']):
            os.remove(response['outputfile'])

    def test_convert(self):
        print 'testing convert'
        dwca = self.framework.dwca
        workspace = self.framework.testdatapath
        outputfile = self.framework.outputfile
        archivetype = self.framework.archivetype

        inputs = {}
        inputs['inputfile'] = dwca
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        inputs['archivetype'] = archivetype
#        print 'inputs:\n%s' % inputs

        response=dwca_core_to_tsv(inputs)
#        print 'response:\n%s' % response
        self.assertEqual(response['rowcount'], 8, 'incorrect number of rows in output')
        self.assertTrue(response['success'], \
            'conversion not successful')

    def test_source_headers_correct(self):
        print 'testing source_headers_correct'
        dwca = self.framework.dwca
        workspace = self.framework.testdatapath
        outputfile = self.framework.outputfile
        archivetype = self.framework.archivetype

        inputs = {}
        inputs['inputfile'] = dwca
        inputs['outputfile'] = outputfile
        inputs['workspace'] = workspace
        inputs['archivetype'] = archivetype

        response=dwca_core_to_tsv(inputs)
#        print 'response:\n%s' % response

        outputfilefullpath = response['outputfile']
        header = read_header(outputfilefullpath, tsv_dialect())
        modelheader = []
        modelheader.append('type')
        modelheader.append('modified')
        modelheader.append('language')
        modelheader.append('accessRights')
        modelheader.append('references')
        modelheader.append('institutionCode')
        modelheader.append('collectionCode')
        modelheader.append('basisOfRecord')
        modelheader.append('informationWithheld')
        modelheader.append('dynamicProperties')
        modelheader.append('occurrenceID')
        modelheader.append('catalogNumber')
        modelheader.append('recordNumber')
        modelheader.append('recordedBy')
        modelheader.append('individualCount')
        modelheader.append('sex')
        modelheader.append('lifeStage')
        modelheader.append('establishmentMeans')
        modelheader.append('preparations')
        modelheader.append('associatedMedia')
        modelheader.append('associatedSequences')
        modelheader.append('associatedTaxa')
        modelheader.append('otherCatalogNumbers')
        modelheader.append('occurrenceRemarks')
        modelheader.append('associatedOccurrences')
        modelheader.append('previousIdentifications')
        modelheader.append('fieldNumber')
        modelheader.append('eventDate')
        modelheader.append('eventTime')
        modelheader.append('endDayOfYear')
        modelheader.append('year')
        modelheader.append('month')
        modelheader.append('day')
        modelheader.append('verbatimEventDate')
        modelheader.append('habitat')
        modelheader.append('samplingProtocol')
        modelheader.append('eventRemarks')
        modelheader.append('higherGeography')
        modelheader.append('continent')
        modelheader.append('waterBody')
        modelheader.append('islandGroup')
        modelheader.append('island')
        modelheader.append('country')
        modelheader.append('stateProvince')
        modelheader.append('county')
        modelheader.append('locality')
        modelheader.append('verbatimLocality')
        modelheader.append('minimumElevationInMeters')
        modelheader.append('maximumElevationInMeters')
        modelheader.append('minimumDepthInMeters')
        modelheader.append('maximumDepthInMeters')
        modelheader.append('locationAccordingTo')
        modelheader.append('locationRemarks')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('geodeticDatum')
        modelheader.append('coordinateUncertaintyInMeters')
        modelheader.append('verbatimCoordinates')
        modelheader.append('verbatimCoordinateSystem')
        modelheader.append('georeferencedBy')
        modelheader.append('georeferencedDate')
        modelheader.append('georeferenceProtocol')
        modelheader.append('georeferenceSources')
        modelheader.append('georeferenceVerificationStatus')
        modelheader.append('identificationQualifier')
        modelheader.append('typeStatus')
        modelheader.append('identifiedBy')
        modelheader.append('dateIdentified')
        modelheader.append('identificationReferences')
        modelheader.append('identificationVerificationStatus')
        modelheader.append('identificationRemarks')
        modelheader.append('scientificName')
        modelheader.append('higherClassification')
        modelheader.append('kingdom')
        modelheader.append('phylum')
        modelheader.append('class')
        modelheader.append('order')
        modelheader.append('family')
        modelheader.append('genus')
        modelheader.append('specificEpithet')
        modelheader.append('infraspecificEpithet')
        modelheader.append('taxonRank')
        modelheader.append('nomenclaturalCode')
        modelheader.append('individualID')
        modelheader.append('rights')

        self.assertEqual(len(header), 85, 'incorrect number of fields in header')
        s = 'Header:\n%s\nnot equal to the model header:\n%s' % (header, modelheader)
        self.assertEqual(header, modelheader, s)

if __name__ == '__main__':
    print '=== dwca_core_to_tsv_test.py ==='
    unittest.main()
