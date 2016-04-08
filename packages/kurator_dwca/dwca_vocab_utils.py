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
__version__ = "dwca_vocab_utils.py 2016-04-08T12:14-03:00"

# This file contains common utility functions for dealing with the vocabulary management
# for Darwin Core-related terms
#
# Example:
#
# python dwca_vocab_utils.py

from dwca_utils import csv_file_dialect
from dwca_utils import read_header
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_terms import simpledwctermlist
from dwca_terms import vocabfieldlist
from dwca_terms import controlledtermlist
from dwca_terms import geogkeytermlist
from dwca_terms import geogvocabextrafieldlist
import os.path
import glob
import unittest
try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

def geogvocabheader():
    # Construct the header row for the geog vocabulary.
    geogkey = compose_key_from_list(geogkeytermlist)
    fieldnames = makevocabheader(geogkey)
    for f in geogvocabextrafieldlist:
        fieldnames.append(f)
    return fieldnames

def makevocabheader(keyfields):
    # Construct the header row for this vocabulary. Begin with a field name
    # equal to the keyfields variable, then add the remaining field names after
    # the first one from the standard vocabfieldlist.
    # Example:
    # if keyfields = 'country|stateprovince|county'
    # and
    # vocabfieldlist = ['verbatim','standard','checked']
    # then the header will end up as 
    # 'country|stateprovince|county','standard','checked'
    if keyfields is None:
        return None

    fieldnames=[]

    # Set the first field to be the string of concatenated field names.
    fieldnames.append(keyfields.replace(' ',''))
    firstfield = True

    # Then add the remaining standard vocab fields.
    for f in vocabfieldlist:
        # in the case of composite key vocabualaries, do not use the first vocab
        # field 'verbatim'. It is being replaced with the keyfields string.
        if firstfield==True:
            firstfield = False
        else:
            fieldnames.append(f)
    return fieldnames

def writevocabheader(fullpath, fieldnames, dialect):
    if fullpath is None or fieldnames is None or len(fullpath) == 0 or \
        len(fieldnames) == 0:
        return False
    with open(fullpath, 'w') as csvfile:
        try:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()
        except:
            return False
    return True

def compose_key_from_list(alist, separator='|'):
    """Get a string consisting of the values in a list, separated by separator value.
    parameters:
        alist - the list of values to compose into a string. The values cannot contain 
            the separator string, which is '|' by default.
        separator - the string to use as the value separator in the string
    returns:
        key - the composed string with values separated by separator
    """
    n=0
    for value in alist:
        if n==0:
            key=value
        else:
            key=key+separator+value
        n+=1
    return key

def vocab_dialect():
    """Get a dialect object with properties for vocabulary management files.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with TSV attributes"""
#     dialect = csv.excel
#     dialect.lineterminator='\r'
#     dialect.delimiter=','
#     dialect.escapechar='/'
#     dialect.doublequote=True
#     dialect.quotechar='"'
#     dialect.quoting=csv.QUOTE_MINIMAL
#     dialect.skipinitialspace=True
#     dialect.strict=False
#     return dialect
    return tsv_dialect()

# def get_standard_value(was, valuedict):
#     """Get the standard value of a term from a dictionary.
#     parameters:
#         was - the value of the term to standardize
#         valuedict - the dictionary to look up the standard value
#     returns:
#         valuedict[was] - the standard value of the term, if it exists, else None"""
#     if was is None:
#         return None
#     if was in valuedict.keys():
#         return valuedict[was]
#     return None

# def get_checked_standard_value(origvalue, vocabdict):
#     """Get the checked standard value of a term from a dictionary.
#     parameters:
#         origvalue - the value of the term to standardize
#         vocabdict - the vocab dictionary in which to look up the standard value
#     returns:
#         standardvalue - the standard value of the term, if it exists, else None"""
#     if origvalue is None:
#         return None
# #    print 'origvalue: %s\nvocabdict:\n%s' % (origvalue,vocabdict)
#     try:
#         vocabrecord = vocabdict[origvalue]
#         if vocabrecord['checked']=='0':
#             # value not vetted
#             return None
#         standardvalue = vocabrecord['standard']
#     except:
#         return None
#     return standardvalue

# def get_differing_standard_value(origvalue, vocabdict):
#     """Get the checked standard value of a term from a dictionary.
#     parameters:
#         origvalue - the value of the term to standardize
#         vocabdict - the vocab dictionary in which to look up the standard value
#     returns:
#         standardvalue - the standard value of the term, if it exists, else None"""
#     standardvalue = get_checked_standard_value(origvalue, vocabdict)
#     if standardvalue is None:
#         # no standard value found
#         return None
#     if origvalue==standardvalue:
#         # value already standard
#         return None
#     return standardvalue
 
# def get_vocab_record(origvalue, vocabdict):
#     """Get the record from the vocabulary dict matching the origvalue
#     parameters:
#         origvalue - the value of the term to standardize
#         vocabdict - the vocabulary (as a dict) in which to lookup the standard value
#     returns:
#         result - None if not found in the vocabulary, otherwise return the full vocabulary 
#             record"""
#     vocabrecord = None
#     try:
#         vocabrecord = vocabdict[origvalue]
#     except:
#         pass
#     return vocabrecord

def matching_vocab_dict_from_file(checklist, vocabfile, dialect=None):
    """Given a checklist of values, get matching values from a vocabulary file.
    parameters:
        checklist - the list of values to get from the vocabfile
        vocabfile - the full path to the vocabulary lookup file
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        vocabdict - a dict of complete vocabulary records matching the values in the 
            checklist
    """
    if checklist is None:
        return None
    vocabdict = vocab_dict_from_file(vocabfile, dialect)
    if vocabdict is None or len(vocabdict)==0:
        return None
    matchingvocabdict = {}
#    print 'checklist: %s\nvocabdict:\/%s' % (checklist, vocabdict)
    for term in checklist:
        if term in vocabdict:
            matchingvocabdict[term]=vocabdict[term]
    return matchingvocabdict

def vocab_dict_from_file(vocabfile, dialect=None):
    """Get a full vocabulary as a dict.
    parameters:
        vocabfile - the full path to the vocabulary lookup file
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        vocabdict - a dict of complete vocabulary records
    """
    if os.path.isfile(vocabfile) == False:
        return None
    vocabdict = {}
    if dialect is None:
        dialect = vocab_dialect()
    with open(vocabfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        i=0
        for row in dr:
            # Skip the header row.
#            print 'row: %s' % row
            if i==0:
                i=1
            else:
                rowdict = {}
                rowdict['standard']=row['standard']
                rowdict['checked']=row['checked']
                rowdict['error']=row['error']
                rowdict['incorrectable']=row['incorrectable']
                rowdict['source']=row['source']
                rowdict['misplaced']=row['misplaced']
                rowdict['comment']=row['comment']
                vocabdict[row['verbatim']]=rowdict
#                print 'rowdict: %s' % rowdict
#    print 'vocabdict=%s' % vocabdict    
    return vocabdict

def term_values_recommended(lookupdict):
    """Get non-standard values and their standard equivalents from a lookupdict
    parameters:
        lookupdict - a dictionary of lookup terms from a vocabulary
    returns:
        recommended - a dictionary of verbatim values and their recommended 
            standardized values
    """
    if lookupdict is None or len(lookupdict)==0:
        return None
    recommended = {}
    for key, value in lookupdict.iteritems():
#        print 'key: %s value: %s' % (key, value)
        if value['checked']=='1':
            if value['standard'] != key:
                recommended[key] = value
    return recommended

def term_recommendation_report(reportfile, recommendationdict, dialect=None):
    """Write a term recommendation report.
    parameters:
        reportfile - the full path to the output report file
        recommendationdict - a dictionary of term recommendations
        dialect - a csv.dialect object with the attributes of the report file
    returns:
        success - True if the report was written, else False
    """
    if recommendationdict is None or len(recommendationdict)==0:
        return False

    if dialect is None:
        dialect = tsv_dialect()

    if reportfile is not None:
        with open(reportfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=vocabfieldlist)
            writer.writeheader()

        if os.path.isfile(reportfile) == False:
            print 'reportfile: %s not created' % reportfile
            return False

#        print 'tokens: %s' % (tokens)
        with open(reportfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=vocabfieldlist)
            for key, value in recommendationdict.iteritems():
#                print ' key: %s value: %s' % (key, value)
                writer.writerow({'verbatim':key, 
                    'standard':value['standard'], \
                    'checked':value['checked'], \
                    'error':value['error'], \
                    'misplaced':value['misplaced'], \
                    'incorrectable':value['incorrectable'], \
                    'source':value['source'], \
                    'comment':value['comment'] })
    else:
        # print the report
        print 'verbatim\tstandard\tchecked\terror\tmisplaced\tincorrectable\tsource\tcomment'
        for key, value in recommendationdict.iteritems():
            print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' ( \
                key,
                value['standard'], \
                value['checked'], \
                value['error'], \
                value['misplaced'], \
                value['incorrectable'], \
                value['source'], \
                value['comment'])
    return True

# def distinct_vocab_list_from_file(vocabfile, dialect=None):
#     """Get the list of distinct verbatim values in an existing vocabulary lookup file.
#     parameters:
#         vocabfile - the full path to the vocabulary lookup file
#         dialect - a csv.dialect object with the attributes of the vocabulary lookup file
#     returns:
#         sorted(list(values)) - a sorted list of distinct verbatim values in the vocabulary
#     """
# #    print 'vocabfile: %s\nvocabfieldlist:%s' % (vocabfile, vocabfieldlist)
#     if os.path.isfile(vocabfile) == False:
#         return None
#     values = set()
#     if dialect is None:
#         dialect = vocab_dialect()
#     with open(vocabfile, 'rU') as csvfile:
#         dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
#         i=0
#         for row in dr:
#             # Skip the header row.
#             if i>0:
#                 values.add(row['verbatim'])
#             i+=1
#     return sorted(list(values))

def distinct_composite_term_values_from_file(inputfile, terms, separator = '|', dialect=None):
    """Get the list of distinct order-specific values of set of terms in a file.
    parameters:
        inputfile - the full path to the input file
        terms - a string containing the field names in the input file to use for the key
        separator - the string that separates the fieldnames in terms
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        list(valueset) - a list of distinct values of the composite term
    """
    if inputfile is None:
        return None
    if os.path.isfile(inputfile) == False:
        return None
    values = set()
    if dialect is None:
        dialect = csv_file_dialect(inputfile)
    header = read_header(inputfile, dialect)
    if header is None:
        return None

    termlist = terms.split(separator)
#    print 'header: %s\ntermlist: %s' % (header, termlist)
    # Iterate over the file rows to get the values of the terms
    with open(inputfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
        i=0
        # Now pull out the values of all the terms in the term composite
        # for every row and add the key to the vocabulary with the values of the 
        # constituent terms.
        for row in dr:
            # Skip the header row.
            if i>0:
                vallist=[]
                for t in termlist:
                    try:
                        v=row[t]
                        vallist.append(v)
                    except:
                        vallist.append('')
                values.add(compose_key_from_list(vallist))
            i+=1
    return list(values)

def distinct_term_values_from_file(inputfile, termname, dialect=None):
    """Get the list of distinct values of a term in a file.
    parameters:
        inputfile - the full path to the input file
        termname - the field name in the header of the input file to search in
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        sorted(list(values)) - a sorted list of distinct values of the term
    """
    if inputfile is None:
        return None
    if os.path.isfile(inputfile) == False:
        return None
    values = set()
    if dialect is None:
        dialect = csv_file_dialect(inputfile)
    header = read_header(inputfile, dialect)
#    print 'header:/n%s' % header
#    print 'dialect:\n%s' % dialect_attributes(dialect)
    if header is None:
        return None
    if termname not in header:
        return None
    with open(inputfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
        i=0
        for row in dr:
            # Skip the header row.
            if i>0:
                values.add(row[termname])
            i+=1
    return sorted(list(values))

def terms_not_in_dwc(checklist):
    """From a list of terms, get those that are not Darwin Core terms.
    parameters:
        checklist - the list of values to check against the targetlist
    returns:
        sorted(list(values)) - a sorted list of non-Darwin Core terms from the checklist
    """
    return not_in_list(simpledwctermlist, checklist)

def not_in_list(targetlist, checklist):
    """Get the list of distinct values in a checklist that are not in a target list.
    parameters:
        targetlist - the list to check to see if the value already exists there
        checklist - the list of values to check against the targetlist
    returns:
        sorted(list(values)) - a sorted list of distinct new values not in the target list
    """
    if checklist is None:
        return None
    if targetlist is None:
        return sorted(checklist)
    newlist = []
    for v in checklist:
        if v not in targetlist:
            newlist.append(v)
    if '' in newlist:
        newlist.remove('')
    return sorted(newlist)

def keys_list(sourcedict):
    if sourcedict is None or len(sourcedict)==0:
        return None
    keylist = []
    for key, value in sourcedict.iteritems():
        keylist.append(key)
    return keylist

def distinct_vocabs_to_file(vocabfile, valuelist, dialect=None):
    """Add distinct new verbatim values from a valuelist to a vocabulary lookup file.
    parameters:
        vocabfile - the full path to the vocabulary lookup file
        valuelist - the list of values to check and add any new ones to the vocabulary
            lookup file
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        newvaluelist - a sorted list of distinct verbatim values added to the vocabulary
            lookup file
    """
    if vocabfile is None:
        return None
    vocablist = distinct_term_values_from_file(vocabfile, 'verbatim', dialect)
    newvaluelist = not_in_list(vocablist, valuelist)
    if newvaluelist is None or len(newvaluelist) == 0:
        return None

    if dialect is None:
        dialect = vocab_dialect()
    if not os.path.isfile(vocabfile):
        with open(vocabfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
            writer.writeheader()

    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        for term in newvaluelist:
            writer.writerow({'verbatim':term, 'standard':'', 'checked':0 })
    return newvaluelist

class DWCAVocabUtilsFramework():
    # testdatapath is the location of example files to test with
    testdatapath = './data/tests/'
    # vocabpath is the location of vocabulary files to test with
    vocabpath = './data/vocabularies/'

    # following are files used as input during the tests, don't remove these
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    monthvocabfile = testdatapath + 'test_vocab_month.txt'
    geogvocabfile = vocabpath + 'dwc_geography.txt'

    # following are files output during the tests, remove these in dispose()
    csvwriteheaderfile = testdatapath + 'test_write_header_file.csv'
    tsvfromcsvfile1 = testdatapath + 'test_tsv_from_csv_1.txt'
    tsvfromcsvfile2 = testdatapath + 'test_tsv_from_csv_2.txt'
    testvocabfile = testdatapath + 'test_vocab_file.csv'
    writevocabheadertestfile = testdatapath + 'test_write_vocabheader.txt'
    reporttestfile = testdatapath + 'test_term_recommended_report.txt'

    def dispose(self):
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        reporttestfile = self.reporttestfile
        if os.path.isfile(csvwriteheaderfile):
            os.remove(csvwriteheaderfile)
        if os.path.isfile(tsvfromcsvfile1):
            os.remove(tsvfromcsvfile1)
        if os.path.isfile(tsvfromcsvfile2):
            os.remove(tsvfromcsvfile2)
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        if os.path.isfile(reporttestfile):
            os.remove(reporttestfile)
        return True

class DWCAVocabUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = DWCAVocabUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        vocabpath = self.framework.vocabpath
        testdatapath = self.framework.testdatapath
        compositetestfile = self.framework.compositetestfile
        monthvocabfile = self.framework.monthvocabfile
        geogvocabfile = self.framework.geogvocabfile
        dialect = vocab_dialect()
        
        for field in controlledtermlist:
            vocabfile = vocabpath + field + '.txt'
            if not os.path.isfile(vocabfile):
                success = writevocabheader(vocabfile, vocabfieldlist, dialect)
            self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

        self.assertTrue(os.path.isfile(geogvocabfile), geogvocabfile + ' does not exist')
        self.assertTrue(os.path.isfile(compositetestfile), compositetestfile + ' does not exist')

    def test_vocab_headers_correct(self):
        print 'testing vocab_headers_correct'
        vocabpath = self.framework.vocabpath
        dialect = vocab_dialect()
        for field in controlledtermlist:
            vocabfile = vocabpath + field + '.txt'
            if not os.path.isfile(vocabfile):
                success = writevocabheader(vocabfile, vocabfieldlist, dialect)
            header = read_header(vocabfile,dialect)
            self.assertEqual(header, vocabfieldlist, vocabfile + ' header not correct')

    def test_read_vocab_header(self):
        print 'testing read_vocab_header'
        dialect = vocab_dialect()
        monthvocabfile = self.framework.monthvocabfile
        header = read_header(monthvocabfile, dialect)
#        print 'len(header)=%s len(model)=%s\nheader:\n%s\nmodel:\n%s' \
#            % (len(header), len(vocabfieldlist), header, vocabfieldlist)
        self.assertEqual(len(header), 8, 'incorrect number of fields in header')
        self.assertEqual(header, vocabfieldlist, 'header not equal to the model header')

    def test_read_geog_header(self):
        print 'testing read_geog_header'
        dialect = vocab_dialect()
        geogvocabfile = self.framework.geogvocabfile
        header = read_header(geogvocabfile, dialect)
        modelheader = []
        modelheader.append('continent|country|countryCode|stateProvince|county|municipality|waterBody|islandGroup|island')
        for f in vocabfieldlist:
            if f != 'verbatim':
                modelheader.append(f)
        for f in geogvocabextrafieldlist:
            modelheader.append(f)
#        print 'len(header)=%s len(model)=%s\nheader:\n%s\nmodel:\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), len(vocabfieldlist) + len(geogvocabextrafieldlist), 
            'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'geog header not equal to the model header')

#     def test_get_standard_value(self):
#         print 'testing get_standard_value'
#         testdict = { 'm':'male', 'M':'male', 'male':'male', 'f':'female', 'F':'female', 
#             'female':'female'}
#         self.assertIsNone(get_standard_value('unnoewn', testdict), 
#             "lookup 'unnoewn' does not return None")
#         self.assertIsNone(get_standard_value(None, testdict), 
#             'lookup None does not return None')
#         self.assertEqual(get_standard_value('m', testdict), 'male', 
#             "lookup 'm' does not return 'male'")
#         self.assertEqual(get_standard_value('M', testdict), 'male', 
#             "lookup 'M' does not return 'male'")
#         self.assertEqual(get_standard_value('male', testdict), 'male', 
#             "lookup 'male' does not return 'male'")
#         self.assertEqual(get_standard_value('f', testdict), 'female', 
#             "lookup 'f' does not return 'female'")
#         self.assertEqual(get_standard_value('F', testdict), 'female', 
#             "lookup 'F' does not return 'female'")
#         self.assertEqual(get_standard_value('female', testdict), 'female', 
#             "lookup 'female' does not return 'female'")

#     def test_get_checked_standard_value(self):
#         print 'testing get_checked_standard_value'
#         monthvocabfile = self.framework.monthvocabfile
#         monthdict = vocab_dict_from_file(monthvocabfile)
# #        print 'monthdict:\n%s' % monthdict
# 
#         soughtvalue = '5'
#         expected = '5'
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = '6'
#         expected = '6'
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'V'
#         expected = '5'
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'v'
#         expected = '5'
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'VI'
#         expected = None
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'Vi'
#         expected = None
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'Vi'
#         expected = None
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'vi'
#         expected = None
#         standardvalue = get_checked_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)

#     def test_get_differing_standard_value(self):
#         print 'testing get_differing_standard_value'
#         monthvocabfile = self.framework.monthvocabfile
#         monthdict = vocab_dict_from_file(monthvocabfile)
# #        print 'monthdict:\n%s' % monthdict
#         
#         soughtvalue = '5'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = '6'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'V'
#         expected = '5'
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'v'
#         expected = '5'
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'VI'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'Vi'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'Vi'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)
# 
#         soughtvalue = 'vi'
#         expected = None
#         standardvalue = get_differing_standard_value(soughtvalue, monthdict)
#         s = 'standard value (%s) of %s not as expected (%s) found in %s' % \
#             (standardvalue, soughtvalue, expected, monthvocabfile)
#         self.assertEqual(standardvalue, expected, s)

#     def test_get_vocab_record(self):
#         print 'testing vocab_dict_from_file'
#         monthvocabfile = self.framework.monthvocabfile
#         monthdict = vocab_dict_from_file(monthvocabfile)
#         vocabrecord = get_vocab_record('V', monthdict)
# #        print 'vocabrecord:\n%s' % vocabrecord
#         self.assertIsNotNone(vocabrecord, 
#             "get_vocab_record for value 'V' returns None")
#         self.assertEqual(vocabrecord['comment'], '', 
#             "value of 'comment' not equal to '' for vocab value 'V'")
#         self.assertEqual(vocabrecord['checked'], '1', 
#             "value of 'checked' not equal to 1 for vocab value 'V'")
#         self.assertEqual(vocabrecord['standard'], '5', 
#             "value of 'standard' not equal to '5' for vocab value 'V'")
#         self.assertEqual(vocabrecord['incorrectable'], '', 
#             "value of 'incorrectable' not equal to '' for vocab value 'V'")
#         self.assertEqual(vocabrecord['source'], '', 
#             "value of 'source' not equal to '' for vocab value 'V'")
#         self.assertEqual(vocabrecord['error'], '', 
#             "value of 'error' not equal to '' for vocab value 'V'")
#         self.assertEqual(vocabrecord['misplaced'], '', 
#             "value of 'misplaced' not equal to '' for vocab value 'V'")

    def test_vocab_dict_from_file(self):
        print 'testing vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        monthdict = vocab_dict_from_file(monthvocabfile)
        expected = 8
#        print 'monthdict:\n%s' % monthdict
        s = 'month vocab at %s has %s items in it instead of %s' % \
            (monthvocabfile, len(monthdict), expected)
        self.assertEqual(len(monthdict), expected, s)

        self.assertTrue('vi' in monthdict,"'vi' not found in month dictionary")
        self.assertEqual(monthdict['vi']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['checked'], '0', 
            "value of 'checked' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['standard'], '', 
            "value of 'standard' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['incorrectable'], '0', 
            "value of 'incorrectable' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['source'], '', 
            "value of 'source' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['error'], '', 
            "value of 'error' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['misplaced'], '0', 
            "value of 'misplaced' not equal to '0' for vocab value 'vi'")

        self.assertTrue('5' in monthdict,"'5' not found in month dictionary")
        self.assertEqual(monthdict['5']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['checked'], '1', 
            "value of 'checked' not equal to 1 for vocab value '5'")
        self.assertEqual(monthdict['5']['standard'], '5', 
            "value of 'standard' not equal to '5' for vocab value '5'")
        self.assertEqual(monthdict['5']['incorrectable'], '', 
            "value of 'incorrectable' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['source'], '', 
            "value of 'source' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['error'], '', 
            "value of 'error' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['misplaced'], '', 
            "value of 'misplaced' not equal to '' for vocab value '5'")

    def test_matching_vocab_dict_from_file(self):
        print 'testing vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        checklist = ['vi', '5', 'fdsf']
        monthdict = matching_vocab_dict_from_file(checklist, monthvocabfile)
#        print 'matchingmonthdict:\n%s' % monthdict
        s = 'month vocab at %s does has %s matching items in it instead of 2' % \
            (monthvocabfile, len(monthdict))
        self.assertEqual(len(monthdict), 2, s)

        self.assertTrue('vi' in monthdict,"'vi' not found in month dictionary")
        self.assertEqual(monthdict['vi']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['checked'], '0', 
            "value of 'checked' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['standard'], '', 
            "value of 'standard' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['incorrectable'], '0', 
            "value of 'incorrectable' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['source'], '', 
            "value of 'source' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['error'], '', 
            "value of 'error' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['misplaced'], '0', 
            "value of 'misplaced' not equal to '0' for vocab value 'vi'")

        self.assertTrue('5' in monthdict,"'5' not found in month dictionary")
        self.assertEqual(monthdict['5']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['checked'], '1', 
            "value of 'checked' not equal to 1 for vocab value '5'")
        self.assertEqual(monthdict['5']['standard'], '5', 
            "value of 'standard' not equal to '5' for vocab value '5'")
        self.assertEqual(monthdict['5']['incorrectable'], '', 
            "value of 'incorrectable' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['source'], '', 
            "value of 'source' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['error'], '', 
            "value of 'error' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['misplaced'], '', 
            "value of 'misplaced' not equal to '' for vocab value '5'")

#     def test_distinct_vocab_list_from_file(self):
#         print 'testing distinct_vocab_list_from_file'
#         monthvocabfile = self.framework.monthvocabfile
#         months = distinct_vocab_list_from_file(monthvocabfile)
# #        print 'months: %s' % months
#         self.assertEqual(len(months), 8, 
#             'the number of distinct verbatim month values does not match expectation')
#         self.assertEqual(months, ['5', '6', 'V', 'VI', 'Vi', 'v', 'vI', 'vi'],
#             'verbatim month values do not match expectation')

    def test_distinct_term_values_from_file(self):
        print 'testing distinct_term_values_from_file'
        monthvocabfile = self.framework.monthvocabfile
        months = distinct_term_values_from_file(monthvocabfile, 'verbatim')
        expected = 8
#        print 'months: %s' % months
        self.assertEqual(len(months), expected, 
            'the number of distinct verbatim month values does not match expectation')
        self.assertEqual(months, ['5', '6', 'V', 'VI', 'Vi', 'v', 'vI', 'vi'],
            'verbatim month values do not match expectation')

    def test_distinct_composite_term_values_from_file(self):
        print 'testing distinct_composite_term_values_from_file'
        testfile = self.framework.compositetestfile
        geogs = distinct_composite_term_values_from_file(testfile, 
            'country', '|')
#        print 'geogs: %s' % geogs
        self.assertEqual(geogs, ['United States'],
            'composite geogs country values do not match expectation')

        geogs = distinct_composite_term_values_from_file(testfile, 
            'country|stateProvince', '|')
#        print 'geogs: %s' % geogs
        self.assertEqual(geogs, ['United States|Colorado', 'United States|California', 
            'United States|Washington', 'United States|Hawaii'],
            'composite geogs country values do not match expectation')

        geogs = distinct_composite_term_values_from_file(testfile, 
            'country|stateprovince|county', '|')
#        print 'geogs: %s' % geogs
        self.assertEqual(geogs, ['United States||San Bernardino', 
            'United States||Honolulu', 'United States||', 'United States||Kern', 
            'United States||Chelan'],
            'composite geogs values do not match expectation')

        geogs = distinct_composite_term_values_from_file(testfile, 
            'country|stateProvince|county', '|')
#        print 'geogs: %s' % geogs
        self.assertEqual(geogs, ['United States|Colorado|', 'United States|California|', 
        'United States|Washington|Chelan', 'United States|Hawaii|Honolulu', 
        'United States|California|San Bernardino', 'United States|California|Kern'],
            'composite geogs values do not match expectation')

    def test_terms_not_in_dwc(self):
        print 'testing terms_not_in_dwc'
        checklist = ['eventDate', 'verbatimEventDate', 'year', 'month', 'day', 
        'earliestDateCollected', '', 'latestDateCollected']
        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['earliestDateCollected', 'latestDateCollected']
        self.assertEqual(notdwc, expectedlist, 'non-dwc terms do not meet expectation')

        checklist = ['catalogNumber','catalognumber']
        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['catalognumber']
#        print 'notdwc: %s\nexpected: %s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, 'catalogNumber DwC test failed')

    def test_not_in_list(self):
        print 'testing not_in_list'
        targetlist = ['b', 'a', 'c']
        checklist = ['c', 'd', 'a', 'e']
        newlist = not_in_list(targetlist, checklist)
#        print 'newlist: %s' % newlist
        self.assertEqual(newlist, ['d', 'e'],
            'new values de for target list do not meet expectation')
        newlist = not_in_list(None, checklist)
        self.assertEqual(newlist, ['a', 'c', 'd', 'e'],
            'new values acde for targetlist do not meet expectation')

    def test_distinct_vocabs_to_file(self):
        print 'testing distinct_vocabs_to_file'
        testvocabfile = self.framework.testvocabfile

        valuelist = ['b', 'a', 'c']
        writtenlist = distinct_vocabs_to_file(testvocabfile, valuelist)
#        print 'writtenlist1: %s' % writtenlist
        self.assertEqual(writtenlist, ['a', 'b', 'c'],
            'new values abc for target list not written to testvocabfile')

        checklist = ['c', 'd', 'a', 'e']
        writtenlist = distinct_vocabs_to_file(testvocabfile, checklist)
#        print 'writtenlist2: %s' % writtenlist
        self.assertEqual(writtenlist, ['d', 'e'],
            'new values de for target list not written to testvocabfile')

        fulllist = distinct_term_values_from_file(testvocabfile, 'verbatim')
#        print 'fulllist: %s' % fulllist
        self.assertEqual(fulllist, ['a', 'b', 'c', 'd', 'e'],
            'full values abcde not found in testvocabfile')

    def test_compose_key_from_list(self):
        print 'testing compose_key_from_list'
        valuelist = ['a', 'b', 'c']
        key = compose_key_from_list(valuelist)
        expected = 'a|b|c'
        self.assertEqual(key, expected, 
            'key value' + key + 'not as expected: ' + expected)
        key = compose_key_from_list(geogkeytermlist)
        expected = 'continent|country|countryCode|stateProvince|county|municipality|waterBody|islandGroup|island'
        self.assertEqual(key, expected, 
            'geog key value:\n' + key + '\nnot as expected:\n' + expected)

    def test_makevocabheader(self):
        print 'testing makevocabheader'
        # Example:
        # if keyfields = 'country|stateprovince|county'
        # and
        # vocabfieldlist = ['verbatim','standard','checked']
        # then the header will end up as 
        # 'country|stateprovince|county','standard','checked'
        keyfields = 'country|stateprovince|county'
        header = makevocabheader(keyfields)
#        print 'vocabheader:\n%s' % header
        expected = ['country|stateprovince|county', 'standard', 'checked', 'error', 
            'misplaced', 'incorrectable', 'source', 'comment']
        s = 'header:\n%s\nnot as expected:\n%s' % (header,expected)
        self.assertEqual(header, expected, s)

    def test_writevocabheader(self):
        print 'testing writevocabheader'
        writevocabheadertestfile = self.framework.writevocabheadertestfile
        fieldnames = ['country|stateprovince|county', 'standard', 'checked', 'error', 
            'misplaced', 'incorrectable', 'source', 'comment']
        dialect = vocab_dialect()
        success = writevocabheader(writevocabheadertestfile, fieldnames, dialect)
        self.assertTrue(success,'vocab header not written')
        
        header = read_header(writevocabheadertestfile)
        expected = ['country|stateprovince|county', 'standard', 'checked', 'error', 
            'misplaced', 'incorrectable', 'source', 'comment']
        s = 'header:\n%s\nfrom file: %s\nnot as expected:\n%s' \
            % (header,writevocabheadertestfile,expected)
        self.assertEqual(header, expected, s)

    def test_geogvocabheader(self):
        print 'testing geogvocabheader'
        header = geogvocabheader()
        expected = [
            'continent|country|countryCode|stateProvince|county|municipality|waterBody|islandGroup|island',
            'standard', 'checked', 'error', 'misplaced', 'incorrectable', 'source', 
            'comment', 'notHigherGeography']
        s = 'geog header:\n%s\nnot as expected:\n%s' \
            % (header, expected)
        self.assertEqual(header, expected, s)

    def test_term_values_recommended(self):
        print 'testing term_values_recommended'
        monthvocabfile = self.framework.monthvocabfile
        monthdict = vocab_dict_from_file(monthvocabfile)
        recommended = term_values_recommended(monthdict)
#        print 'monthdict:\n%s\nrecommended:\n%s' % (monthdict, recommended)
        expected = {
            'v': {'comment': '', 'checked': '1', 'standard': '5', 
                'incorrectable': '', 'source': '', 'error': '', 'misplaced': ''},
            'V': {'comment': '', 'checked': '1', 'standard': '5', 
                'incorrectable': '', 'source': '', 'error': '', 'misplaced': ''} 
                }
        s = 'added_values:\n%s\nnot as expected:\n%s' \
            % (recommended, expected)
        self.assertEqual(recommended, expected, s)

    def test_term_recommendation_report(self):
        print 'testing term_recommendation_report'
        monthvocabfile = self.framework.monthvocabfile
        reportfile = self.framework.reporttestfile
        monthdict = vocab_dict_from_file(monthvocabfile)
        recommended = term_values_recommended(monthdict)
        success = term_recommendation_report(reportfile, recommended)
        s = 'term recommendation report (%s) not written successfully' % reportfile
        self.assertTrue(success, s)

if __name__ == '__main__':
    unittest.main()
