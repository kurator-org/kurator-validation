#!/usr/bin/env python

# Copyright 2015 President and Fellows of Harvard College
#
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
__version__ = "dwca_terms.py 2016-01-28T13:27:-03:00"

# This file contains definitions of standard lists of terms to be used in composite term
# processing.

# Terms that make up a distinct geography combination
geogkeytermlist = [
    'continent', 'country', 'stateProvince', 'county', 'municipality', 'waterBody', 
    'islandGroup', 'island']

# Terms expected in the standardized output from the geography vocabulary
geogvocaboutputlist = [
    'continent', 'country', 'countrycode', 'stateProvince', 'county', 'municipality', 
    'waterBody', 'islandGroup', 'island', 'verbatimcontinent', 'verbatimcountry', 
    'verbatim_countrycode', 'verbatim_stateProvince', 'verbatim_county', 
    'verbatim_municipality', 'verbatim_waterBody', 'verbatim_islandGroup', 
    'verbatim_island']

# The taxonkeytermlist contains the terms that make up a distinct taxon name combination
taxonkeytermlist = [
    'kingdom', 'genus', 'subgenus', 'specificEpithet', 'infraspecificEpithet', 
    'scientificNameAuthorship', 'scientificName']

# Terms that make up a distinct event combination
eventkeytermlist = [
    'eventdate', 'verbatimeventdate','year','month','day']

# Terms that make up a distinct coordinates combination
coordinateskeytermlist = [
    'decimallatitude', 'decimallongitude', 'verbatimlatitude','verbatimlongitude',
    'verbatimcoordinates']

# For each term in the controlledtermlist there should be a vocabulary file with the
# name [term].csv in which there are three columns: verbatim, standard, checked
controlledtermlist = [
    'type', 'language', 'license', 'basisOfRecord', 'sex', 'lifeStage', 
    'reproductiveCondition', 'establishmentMeans', 'occurrenceStatus', 'preparations', 
    'disposition', 'organismScope', 'month', 'day', 'geodeticDatum', 
    'georeferenceVerificationStatus', 'identificationQualifier', 'typeStatus', 
    'identificationVerificationStatus', 'taxonRank', 'nomenclaturalCode', 
    'taxonomicStatus', 'nomenclaturalStatus']	
    
vocabfieldlist = ['verbatim','standardizedkey', 'checked', 'error','misplaced','incorrectable',
    'source']
