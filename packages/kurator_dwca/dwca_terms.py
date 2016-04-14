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
__version__ = "dwca_terms.py 2016-03-04T11:44-03:00"

# This file contains definitions of standard sets of Darwin Core terms.

# Terms that make up the current Simple Darwin Core
simpledwctermlist = [
    'type','modified','language','license','rightsHolder','accessRights',
    'bibliographicCitation','references','institutionID','collectionID','datasetID',
    'institutionCode','collectionCode','datasetName','ownerInstitutionCode',
    'basisOfRecord','informationWithheld','dataGeneralizations','dynamicProperties',
    'occurrenceID','catalogNumber','recordNumber','recordedBy','individualCount',
    'organismQuantity','organismQuantityType','sex','lifeStage','reproductiveCondition',
    'behavior','establishmentMeans','occurrenceStatus','preparations','disposition',
    'associatedMedia','associatedReferences','associatedSequences','associatedTaxa',
    'otherCatalogNumbers','occurrenceRemarks','organismID','organismName',
    'organismScope','associatedOccurrences','associatedOrganisms',
    'previousIdentifications','organismRemarks','materialSampleID',
    'eventID','parentEventID','fieldNumber','eventDate','eventTime','startDayOfYear',
    'endDayOfYear','year','month','day','verbatimEventDate','habitat','samplingProtocol',
    'samplingEffort','sampleSizeValue','sampleSizeUnit','fieldNotes','eventRemarks',
    'locationID','higherGeographyID','higherGeography','continent','waterBody',
    'islandGroup','island','country','countryCode','stateProvince','county',
    'municipality','locality','verbatimLocality','minimumElevationInMeters',
    'maximumElevationInMeters','verbatimElevation','minimumDepthInMeters',
    'maximumDepthInMeters','verbatimDepth','minimumDistanceAboveSurfaceInMeters',
    'maximumDistanceAboveSurfaceInMeters','locationAccordingTo','locationRemarks',
    'decimalLatitude','decimalLongitude','geodeticDatum','coordinateUncertaintyInMeters',
    'coordinatePrecision','pointRadiusSpatialFit','verbatimCoordinates',
    'verbatimLatitude','verbatimLongitude','verbatimCoordinateSystem','verbatimSRS',
    'footprintWKT','footprintSRS','footprintSpatialFit','georeferencedBy',
    'georeferencedDate','georeferenceProtocol','georeferenceSources',
    'georeferenceVerificationStatus','georeferenceRemarks',
    'geologicalContextID','earliestEonOrLowestEonothem','latestEonOrHighestEonothem',
    'earliestEraOrLowestErathem','latestEraOrHighestErathem',
    'earliestPeriodOrLowestSystem','latestPeriodOrHighestSystem',
    'earliestEpochOrLowestSeries','latestEpochOrHighestSeries','earliestAgeOrLowestStage',
    'latestAgeOrHighestStage','lowestBiostratigraphicZone','highestBiostratigraphicZone',
    'lithostratigraphicTerms','group','formation','member','bed',
    'identificationID','identificationQualifier','typeStatus','identifiedBy',
    'dateIdentified','identificationReferences','identificationVerificationStatus',
    'identificationRemarks',
    'taxonID','scientificNameID','acceptedNameUsageID','parentNameUsageID',
    'originalNameUsageID','nameAccordingToID','namePublishedInID','taxonConceptID',
    'scientificName','acceptedNameUsage','parentNameUsage','originalNameUsage',
    'nameAccordingTo','namePublishedIn','namePublishedInYear','higherClassification',
    'kingdom','phylum','class','order','family','genus','subgenus','specificEpithet',
    'infraspecificEpithet','taxonRank','verbatimTaxonRank','scientificNameAuthorship',
    'vernacularName','nomenclaturalCode','taxonomicStatus','nomenclaturalStatus',
    'taxonRemarks']

# Terms that make up a distinct geography combination
geogkeytermlist = [
    'continent', 'country', 'countryCode', 'stateProvince', 'county', 'municipality', 
    'waterBody', 'islandGroup', 'island']

# Extra terms expected in the standardized geography vocabulary
geogvocabextrafieldlist = ['notHigherGeography']

# The taxonkeytermlist contains the terms that make up a distinct taxon name combination
taxonkeytermlist = [
    'kingdom', 'genus', 'subgenus', 'specificEpithet', 'infraspecificEpithet', 
    'scientificNameAuthorship', 'scientificName']

# Terms that make up a distinct event date combination
eventkeytermlist = [
    'eventdate', 'verbatimeventdate','year','month','day']

# Terms that make up a distinct coordinates combination
coordinateskeytermlist = [
    'decimallatitude', 'decimallongitude', 'verbatimlatitude','verbatimlongitude',
    'verbatimcoordinates']

# Terms that are recommended comply with a controlled vocabulary
controlledtermlist = [
    'type', 'language', 'license', 'basisOfRecord', 'sex', 'lifeStage', 
    'reproductiveCondition', 'establishmentMeans', 'occurrenceStatus', 'preparations', 
    'disposition', 'organismScope', 'month', 'day', 'geodeticDatum', 
    'georeferenceVerificationStatus', 'identificationQualifier', 'typeStatus', 
    'identificationVerificationStatus', 'taxonRank', 'nomenclaturalCode', 
    'taxonomicStatus', 'nomenclaturalStatus']	

# Fields in the header of a vocabulary lookup file
vocabfieldlist = ['verbatim', 'standard', 'checked', 'error', 'misplaced',
    'incorrectable', 'source', 'comment']

# Darwin Cloud terms - concepts commonly found in source data that can be processed into 
# Darwin Core
darwincloudterms = [
    ]