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
__version__ = "text_file_aggregator_test.py 2016-04-05T14:24-03:00"

from text_file_aggregator import text_file_aggregator
from dwca_utils import split_path
import os
import csv
import glob
import json
import unittest

# This file contains unit test for the text_file_aggregator function.
#
# Example:
#
# python text_file_aggregator_test.py

class TextFileAggregatorFramework():
    """Test framework for the text file aggregator."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'
    csvcompositepath = testdatapath + 'test_csv*.csv'
    tsvcompositepath = testdatapath + 'test_tsv*.txt'
    mixedcompositepath = testdatapath + 'test_*_specimen_records.*'

    # test file for aggregation
    tsvfile = testdatapath + 'aggregatedfile.txt'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        removeme = self.testdatapath + self.tsvfile
        if os.path.isfile(removeme):
            os.remove(removeme)
        return True

class TextFileAggregatorTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = TextFileAggregatorFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        inputpath = self.framework.csvcompositepath

        inputs = {}
        response=json.loads(text_file_aggregator(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertEquals(response['aggregaterowcount'], None, \
            'rows written without input path')
        self.assertFalse(response['success'], \
            'aggregation successful without input path')

        inputs['inputpath'] = inputpath
        response=json.loads(text_file_aggregator(json.dumps(inputs)))
#        print 'response:\n%s' % response
        self.assertEquals(response['aggregaterowcount'], None, \
            'rows written without output path')
        self.assertFalse(response['success'], \
            'aggregation successful without output path')

    def test_aggregate_tsvs(self):
        print 'testing aggregate_tsvs'
        tsvfile = self.framework.tsvfile
        tsvcompositepath = self.framework.tsvcompositepath
        inputs = {}
        inputs['inputpath'] = tsvcompositepath
        inputs['aggregatedfile'] = tsvfile
        inputs['inputdialect'] = 'tsv'

        # Aggregate text file
        response=json.loads(text_file_aggregator(json.dumps(inputs)))

#        print 'inputs:\n%s\nresponse:\n%s' % (inputs, response)
        self.assertTrue(os.path.isfile(tsvfile), tsvfile + ' does not exist')
        self.assertEqual(response['aggregaterowcount'], 6, 'incorrect number of rows')

        header = response['aggregateheader']
        modelheader = []
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('locality')
        modelheader.append('materialSampleID')
        modelheader.append('phylum')
        modelheader.append('principalInvestigator')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_aggregate_csvs(self):
        print 'testing aggregate_csvs'
        tsvfile = self.framework.tsvfile
        csvcompositepath = self.framework.csvcompositepath
        inputs = {}
        inputs['inputpath'] = csvcompositepath
        inputs['aggregatedfile'] = self.framework.tsvfile
        inputs['inputdialect'] = 'csv'

        # Aggregate text file
        response=json.loads(text_file_aggregator(json.dumps(inputs)))

        self.assertTrue(os.path.isfile(tsvfile), tsvfile + ' does not exist')
        self.assertEqual(response['aggregaterowcount'], 6, 'incorrect number of rows')

        header = response['aggregateheader']
        modelheader = []
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('locality')
        modelheader.append('materialSampleID')
        modelheader.append('phylum')
        modelheader.append('principalInvestigator')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_aggregate_mix(self):
        print 'testing aggregate_mix'
        tsvfile = self.framework.tsvfile
        mixedcompositepath = self.framework.mixedcompositepath
        inputs = {}
        inputs['inputpath'] = mixedcompositepath
        inputs['aggregatedfile'] = self.framework.tsvfile

        # Aggregate text file
        response=json.loads(text_file_aggregator(json.dumps(inputs)))

        self.assertTrue(os.path.isfile(tsvfile), tsvfile + ' does not exist')
        self.assertEqual(response['aggregaterowcount'], 11, 'incorrect number of rows')

        header = response['aggregateheader']
        modelheader = []
        modelheader.append('BCID')
        modelheader.append('CollectionCode')
        modelheader.append('DatasetName')
        modelheader.append('Id')
        modelheader.append('InstitutionCode')
        modelheader.append('associatedMedia')
        modelheader.append('associatedReferences')
        modelheader.append('associatedSequences')
        modelheader.append('associatedTaxa')
        modelheader.append('basisOfIdentification')
        modelheader.append('catalogNumber')
        modelheader.append('class')
        modelheader.append('coordinateUncertaintyInMeters')
        modelheader.append('country')
        modelheader.append('county')
        modelheader.append('day')
        modelheader.append('dayCollected')
        modelheader.append('dayIdentified')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('establishmentMeans')
        modelheader.append('eventRemarks')
        modelheader.append('extractionID')
        modelheader.append('family')
        modelheader.append('fieldNotes')
        modelheader.append('fieldNumber')
        modelheader.append('fundingSource')
        modelheader.append('geneticTissueType')
        modelheader.append('genus')
        modelheader.append('geodeticDatum')
        modelheader.append('georeferenceProtocol')
        modelheader.append('habitat')
        modelheader.append('identifiedBy')
        modelheader.append('island')
        modelheader.append('islandGroup')
        modelheader.append('length')
        modelheader.append('lifeStage')
        modelheader.append('locality')
        modelheader.append('materialSampleID')
        modelheader.append('maximumDepthInMeters')
        modelheader.append('maximumDistanceAboveSurfaceInMeters')
        modelheader.append('microHabitat')
        modelheader.append('minimumDepthInMeters')
        modelheader.append('minimumDistanceAboveSurfaceInMeters')
        modelheader.append('month')
        modelheader.append('monthCollected')
        modelheader.append('monthIdentified')
        modelheader.append('occurrenceID')
        modelheader.append('occurrenceRemarks')
        modelheader.append('order')
        modelheader.append('permitInformation')
        modelheader.append('phylum')
        modelheader.append('plateID')
        modelheader.append('preservative')
        modelheader.append('previousIdentifications')
        modelheader.append('previousTissueID')
        modelheader.append('principalInvestigator')
        modelheader.append('recordedBy')
        modelheader.append('reproductiveCondition')
        modelheader.append('sampleOwnerInstitutionCode')
        modelheader.append('samplingProtocol')
        modelheader.append('scientificName')
        modelheader.append('scientificNameAuthorship')
        modelheader.append('sex')
        modelheader.append('species')
        modelheader.append('stateProvince')
        modelheader.append('subSpecies')
        modelheader.append('substratum')
        modelheader.append('taxonRemarks')
        modelheader.append('tissueStorageID')
        modelheader.append('vernacularName')
        modelheader.append('weight')
        modelheader.append('wellID')
        modelheader.append('wormsID')
        modelheader.append('year')
        modelheader.append('yearCollected')
        modelheader.append('yearIdentified')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 77, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

if __name__ == '__main__':
    unittest.main()
