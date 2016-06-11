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
__version__ = "geog_recommendation_reporter_test.py 2016-06-11T19:04-03:00"

# This file contains unit tests for the geog_recommendation_reporter function.
#
# Example:
#
# python geog_recommendation_reporter_test.py

from geog_recommendation_reporter import geog_recommendation_reporter
from dwca_utils import read_header
from dwca_utils import csv_file_dialect
from dwca_utils import csv_dialect
from dwca_terms import geogvocabfieldlist
import os
import csv
import unittest

class GeogRecommendationReporterFramework():
    """Test framework for the term recommendation reporter."""
    # location for the test inputs and outputs
    testdatapath = './data/tests/'

    # input data files to tests, don't remove these
    inputfile_onegood = testdatapath + 'test_geog_one_good.csv'
    inputfile_onebad = testdatapath + 'test_geog_one_bad.csv'
    inputfile_onegoodonebad = testdatapath + 'test_geog_one_good_one_bad.csv'
    vocabfile = testdatapath + 'test_geography.txt'

    # output data files from tests, remove these in dispose()
    testgeogreportfile = 'test_geog_recommendation_file.csv'
    testgeogrowreportfile = 'test_geog_row_recommendation_file.csv'
    testreportformat = 'csv'

    def dispose(self):
        """Remove any output files created as a result of testing"""
        testgeogreportfile = self.testdatapath + self.testgeogreportfile
        if os.path.isfile(testgeogreportfile):
            os.remove(testgeogreportfile)
        testgeogrowreportfile = self.testdatapath + self.testgeogrowreportfile
        if os.path.isfile(testgeogrowreportfile):
            os.remove(testgeogrowreportfile)
        return True

class GeogRecommendationReporterTestCase(unittest.TestCase):
    """Unit tests."""
    def setUp(self):
        self.framework = GeogRecommendationReporterFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        inputfile_onegood = self.framework.inputfile_onegood
        inputfile_onebad = self.framework.inputfile_onebad
        inputfile_onegoodonebad = self.framework.inputfile_onegoodonebad
        vocabfile = self.framework.vocabfile
        file = inputfile_onegood
        s =  '%s does not exist' % file
        self.assertTrue(os.path.isfile(file), s)

        file = inputfile_onebad
        s =  '%s does not exist' % file
        self.assertTrue(os.path.isfile(file), s)

        file = inputfile_onegoodonebad
        s =  '%s does not exist' % file
        self.assertTrue(os.path.isfile(file), s)

        self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

    def test_missing_parameters(self):
        print 'testing missing_parameters'
        inputfile_onegood = self.framework.inputfile_onegood
        inputfile_onebad = self.framework.inputfile_onebad
        inputfile_onegoodonebad = self.framework.inputfile_onegoodonebad
        vocabfile = self.framework.vocabfile

        # Test with missing required inputs
        # Test with no inputs
        inputs = {}
        response=geog_recommendation_reporter(inputs)
#        print 'response1:\n%s' % response
        s = 'success without any required inputs'
        self.assertFalse(response['success'], s)

        # Test with missing inputfile
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response2:\n%s' % response
        s = 'success without inputfile'
        self.assertFalse(response['success'], s)

        # Test with missing vocabfile
        inputs = {}
        inputs['inputfile'] = inputfile_onebad
        response=geog_recommendation_reporter(inputs)
#        print 'response3:\n%s' % response
        s = 'success without vocabfile'
        self.assertFalse(response['success'], s)

        # Test with missing optional inputs and an input file with one non-standard geog
        inputs = {}
        inputs['inputfile'] = inputfile_onebad
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response4:\n%s' % response
        s = 'no output files produced with required inputs and a non-standard geog'
        self.assertTrue(response['success'], s)
        # Remove the files created by this test, as the Framework does not know about it
        if os.path.isfile(response['geogoutputfile']):
            os.remove(response['geogoutputfile'])
        if os.path.isfile(response['geogrowoutputfile']):
            os.remove(response['geogrowoutputfile'])

        # Test with missing optional inputs and an input file with one standard geog
        inputs = {}
        inputs['inputfile'] = inputfile_onegood
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response5:\n%s' % response
        s = 'output files produced with required inputs and no non-standard geog'
        self.assertFalse(response['success'], s)
        # Remove the files created by this test, as the Framework does not know about it
        if os.path.isfile(response['geogoutputfile']):
            os.remove(response['geogoutputfile'])
        if os.path.isfile(response['geogrowoutputfile']):
            os.remove(response['geogrowoutputfile'])

        # Test with missing optional inputs and an input file with one standard geog
        # and one non-standard geog
        inputs = {}
        inputs['inputfile'] = inputfile_onegoodonebad
        inputs['vocabfile'] = vocabfile
        response=geog_recommendation_reporter(inputs)
#        print 'response6:\n%s' % response
        s = 'no output files produced with required inputs, a non-standard geog, and a'
        s += ' standard geog'
        self.assertTrue(response['success'], s)
        # Remove the files created by this test, as the Framework does not know about it
        if os.path.isfile(response['geogoutputfile']):
            os.remove(response['geogoutputfile'])
        if os.path.isfile(response['geogrowoutputfile']):
            os.remove(response['geogrowoutputfile'])

    def test_geog_recommendation_reporter(self):
        print 'testing geog_recommendation_reporter'
        inputfile_onebad = self.framework.inputfile_onebad
        inputfile_onegoodonebad = self.framework.inputfile_onegoodonebad
        # No need to test inputfile_onegood, it is not supposed to produce reports
        # and that was tested in test_missing_parameters()

        testgeogreportfile = self.framework.testgeogreportfile
        testgeogrowreportfile = self.framework.testgeogrowreportfile
        vocabfile = self.framework.vocabfile
        workspace = self.framework.testdatapath
        
        # Run tests for file with one record with non-standard geog that is vetted in
        # the geog vocabulary file
        inputs = {}
        inputs['inputfile'] = inputfile_onebad
        inputs['geogoutputfile'] = testgeogreportfile
        inputs['geogrowoutputfile'] = testgeogrowreportfile
        inputs['vocabfile'] = vocabfile
        inputs['workspace'] = workspace

        # Create the reports
        response=geog_recommendation_reporter(inputs)
#        print 'response:\n%s' % response
        success = response['success']
        s = 'geog recommendation failed: %s' % response['message']
        self.assertTrue(success, s)

        # Reports supposedly written, check to see if the files exist
        geogfile = response['geogoutputfile']
        s = '%s not produced with %s' % (geogfile, inputs['inputfile'])
        self.assertTrue(os.path.isfile(geogfile), s)

        geogrowfile = response['geogrowoutputfile']
        s = '%s not produced with %s' % (geogrowfile, inputs['inputfile'])
        self.assertTrue(os.path.isfile(geogrowfile), s)

        # Reports supposedly exists, check the geog file header
        header = read_header(geogfile)
        expected = geogvocabfieldlist
        s = 'geog file %s ' % geogfile
        s += ' header:\n%s\n' % header
        s += 'does not match expected:\n%s' % expected
        self.assertEqual(header, expected)

        # Check the geogrow file header
        rowheader = read_header(geogrowfile)
        expected = ['catalogNumber', 'continent', 'country', 'countryCode', 
            'stateProvince', 'county', 'recommendedgeography', 'new_continent',
            'new_country', 'new_countryCode', 'new_stateProvince', 'new_county',
            'new_municipality', 'new_waterBody', 'new_islandGroup', 'new_island']
        s = 'geogrow file %s ' % geogrowfile
        s += ' header:\n%s\n' % rowheader
        s += 'does not match expected:\n%s' % expected
        self.assertEqual(rowheader, expected)

        geogkey = None
        checked = None
        incorrectable = None
        continent = None
        country = None
        countrycode = None
        stateprovince = None
        county = None
        municipality = None
        waterbody = None
        islandgroup = None
        island = None
        error = None
        comment = None

        dialect = csv_file_dialect(geogfile)
        with open(geogfile, 'rU') as csvfile:
            dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
            # Read the header
            dr.next()
            i = 0
            for row in dr:
#                print 'file: %s row: %s' % (geogfile, row)
                i += 1
                if i == 1:
                    geogkey = row['geogkey']
                    checked = row['checked']
                    incorrectable = row['incorrectable']
                    continent = row['continent']
                    country = row['country']
                    countrycode = row['countryCode']
                    stateprovince = row['stateProvince']
                    county = row['county']
                    municipality = row['municipality']
                    waterbody = row['waterBody']
                    islandgroup = row['islandGroup']
                    island = row['island']
                    error = row['error']
                    comment = row['comment']

        # Check that the geog file has one row
        s = 'geog file %s has %s rows, not 1' % (geogfile, i)
        self.assertEqual(i, 1)

        field = 'geogkey'
        found = geogkey
        expected = '|United States||Washington|Chelan Co.||||'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'checked'
        found = checked
        expected = '1'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'incorrectable'
        found = incorrectable
        expected = '0'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'continent'
        found = continent
        expected = 'North America'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'country'
        found = country
        expected = 'United States'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'countryCode'
        found = countrycode
        expected = 'US'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'stateProvince'
        found = stateprovince
        expected = 'Washington'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'county'
        found = county
        expected = 'Chelan'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'municipality'
        found = municipality
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'waterBody'
        found = waterbody
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'islandGroup'
        found = islandgroup
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'island'
        found = island
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        # Run tests for file with one record with standard geog and on record with a 
        # non-standard geog that is vetted in the geog vocabulary file
        inputs['inputfile'] = inputfile_onegoodonebad

        catalognumber = None
        continent = None
        country = None
        countrycode = None
        stateprovince = None
        county = None
        recommendedgeography = None
        new_continent = None
        new_country = None
        new_countryCode = None
        new_stateProvince = None
        new_county = None
        new_municipality = None
        new_waterBody = None
        new_islandGroup = None
        new_island = None

        dialect = csv_file_dialect(geogrowfile)
        with open(geogrowfile, 'rU') as csvfile:
            dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=rowheader)
            # Read the header
            dr.next()
            i = 0
            for row in dr:
#                print 'file: %s row: %s' % (geogrowfile, row)
                i += 1
                if i == 1:
                    catalognumber = row['catalogNumber']
                    continent = row['continent']
                    country = row['country']
                    countrycode = row['countryCode']
                    stateprovince = row['stateProvince']
                    county = row['county']
                    recommendedgeography = row['recommendedgeography']
                    new_continent = row['new_continent']
                    new_country = row['new_country']
                    new_countrycode = row['new_countryCode']
                    new_stateprovince = row['new_stateProvince']
                    new_county = row['new_county']
                    new_municipality = row['new_municipality']
                    new_waterbody = row['new_waterBody']
                    new_islandgroup = row['new_islandGroup']
                    new_island = row['new_island']

        # Check that the geog file has one row
        s = 'geog file %s has %s rows, not 1' % (geogfile, i)
        self.assertEqual(i, 1)

        field = 'catalogNumber'
        found = catalognumber
        expected = '2'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'continent'
        found = continent
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'country'
        found = country
        expected = 'United States'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'countryCode'
        found = countrycode
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'stateProvince'
        found = stateprovince
        expected = 'Washington'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'county'
        found = county
        expected = 'Chelan Co.'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'municipality'
        found = municipality
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'waterBody'
        found = waterbody
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'islandGroup'
        found = islandgroup
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'island'
        found = island
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'recommendedgeography'
        found = recommendedgeography
        expected = 'North America|United States|US|Washington|Chelan||||'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_continent'
        found = new_continent
        expected = 'North America'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_country'
        found = new_country
        expected = 'United States'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_countryCode'
        found = new_countrycode
        expected = 'US'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_stateProvince'
        found = new_stateprovince
        expected = 'Washington'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_county'
        found = new_county
        expected = 'Chelan'
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_municipality'
        found = new_municipality
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_waterBody'
        found = new_waterbody
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_islandGroup'
        found = new_islandgroup
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

        field = 'new_island'
        found = new_island
        expected = ''
        s = '%s:\n%s does not match expected:\n%s' % (field, found, expected)
        self.assertEqual(found, expected)

if __name__ == '__main__':
    print '=== geog_recommendation_reporter_test.py ==='
    unittest.main()
