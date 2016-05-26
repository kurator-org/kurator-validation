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
__version__ = "dwca_vocab_utils.py 2016-05-26T08:28-03:00"

# This file contains common utility functions for dealing with the vocabulary management
# for Darwin Core-related terms
#
# Example:
#
# python dwca_vocab_utils.py

from dwca_utils import csv_file_dialect
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_utils import slugify
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_terms import simpledwctermlist
from dwca_terms import vocabfieldlist
from dwca_terms import controlledtermlist
from dwca_terms import geogkeytermlist
from dwca_terms import geogvocabfieldlist
from operator import itemgetter
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
    ''' Construct a header row for the geog vocabulary.
    parameters:
        None
    returns:
        fieldnames -  a list of field names in the header
    '''
    geogkey = compose_key_from_list(geogkeytermlist)
    fieldnames = []
    fieldnames.append(geogkey)

    for f in geogvocabfieldlist:
        if f != 'geogkey':
            fieldnames.append(f)

    return fieldnames

def makevocabheader(keyfields):
    ''' Construct the header row for a vocabulary file. Begin with a field name equal to 
    the keyfields variable, then add the remaining field names after the first one from 
    the standard vocabfieldlist.
    parameters:
        keyfields - string of fields concatenated with a separator (required)
    returns:
        fieldnames - list of field names
    # Example:
    # if keyfields = 'country|stateprovince|county'
    # and
    # vocabfieldlist = ['verbatim','standard','checked']
    # then the header will end up as 
    # 'country|stateprovince|county','standard','checked'
    '''
    if keyfields is None or len(keyfields)==0:
#        print 'No key fields string given in makevocabheader()'
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
    ''' Write a vocabulary header to a file.
    parameters:
        fullpath - the full path to the file to write into (required)
        fieldnames - list of field names in the header (required)
        dialect - a csv.dialect object with the attributes of the input file (optional)
    returns:
        success - True if the header was written to the file, otherwise False
    '''
    if fullpath is None or len(fullpath) == 0:
#        print 'No vocabulary file given in writevocabheader().'
        return False

    if fieldnames is None or len(fieldnames) == 0:
#        print 'No list of field names given in writevocabheader().'
        return False

    if dialect is None:
        dialect = tsv_dialect()

    with open(fullpath, 'w') as outfile:
        try:
            writer = csv.DictWriter(outfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()
        except:
#            print 'No header written to file %s in writevocabheader()' % fullpath
            return False

    return True

def compose_key_from_list(alist, separator='|'):
    """Get a string consisting of the values in a list, separated by separator.
    parameters:
        alist - list of values to compose into a string. The values cannot contain 
            the separator string (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        key - composed string with values separated by separator
    """
    if alist is None or len(alist)==0:
#        print 'No list given in compose_key_from_list()'
        return None

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
    return tsv_dialect()

def matching_vocab_dict_from_file(checklist, vocabfile, dialect=None):
    """Given a checklist of values, get matching values from a vocabulary file.
    parameters:
        checklist - list of values to get from the vocabfile (required)
        vocabfile - full path to the vocabulary lookup file (required)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file 
            (default None)
    returns:
        matchingvocabdict - dictionary of complete vocabulary records matching the values 
            in the checklist
    """
    if checklist is None or len(checklist)==0:
#        print 'No list of values given in matching_vocab_dict_from_file()'
        return None

    vocabdict = vocab_dict_from_file(vocabfile, dialect)
    if vocabdict is None or len(vocabdict)==0:
#        print 'No vocabdict constructed in matching_vocab_dict_from_file()'
        return None

    matchingvocabdict = {}

    for term in checklist:
        if term in vocabdict:
            matchingvocabdict[term]=vocabdict[term]

    return matchingvocabdict

def vocab_dict_from_file(vocabfile, dialect=None):
    """Get a vocabulary as a dictionary from a file.
    parameters:
        vocabfile - path to the vocabulary file (required)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        vocabdict - dictionary of complete vocabulary records
    """
    if vocabfile is None or len(vocabfile) == 0:
#        print 'No vocabulary file given in vocab_dict_from_file().'
        return False

    if os.path.isfile(vocabfile) == False:
#        print 'Vocabulary file %s not found in vocab_dict_from_file().' % vocabfile
        return None

    vocabdict = {}

    if dialect is None:
        dialect = vocab_dialect()

    with open(vocabfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        # Read the header
        dr.next()
        for row in dr:
            rowdict = {}
            rowdict['standard']=row['standard']
            rowdict['checked']=row['checked']
            rowdict['error']=row['error']
            rowdict['incorrectable']=row['incorrectable']
            rowdict['source']=row['source']
            rowdict['misplaced']=row['misplaced']
            rowdict['comment']=row['comment']
            vocabdict[row['verbatim']]=rowdict

    return vocabdict

def term_values_recommended(lookupdict):
    """Get non-standard values and their standard equivalents from a lookupdict
    parameters:
        lookupdict - dictionary of lookup terms from a vocabulary (required)
    returns:
        recommended - dictionary of verbatim values and their recommended equivalents
    """
    if lookupdict is None or len(lookupdict)==0:
#        print 'No lookup dictionary given in term_values_recommended().'
        return None

    recommended = {}

    for key, value in lookupdict.iteritems():
        if value['checked']=='1':
            if value['standard'] != key:
                recommended[key] = value

    return recommended

def prefix_keys(d, prefix='new_'):
    ''' Change the keys in a dictionary by adding a prefix to each one.
    parameters:
        d - dictionary (required)
        prefix - string to prepend to key names (default 'new_')
    returns:
        newd - dictionary with replaced keys
    '''
    if d is None or len(d)==0:
#        print 'No dictionary given in prefix_keys().'
        return None

    newd = {}

    for k in d:
        newd[prefix+k]=d[k]

    return newd

def compose_dict_from_key(key, termlist, separator='|'):
    ''' Create a dictionary from a composite key and a list of terms names in the key.
    parameters:
        key - string with the composite values of terms (required) 
            (e.g., '|United States|US')
        termlist - field names for the values in the key (required)
            (e.g., ['continent', 'country', 'countryCode'])
        separator - string separating the values in the key (default '|')
    returns:
        d - dictionary of fields and their values 
            (e.g., {'continent':'', 'country':'United States', 'countryCode':'US' } )
    '''
    if key is None or len(key)==0:
#        print 'No key given in compose_dict_from_key()'
        return None

    if termlist is None or len(termlist)==0:
#        print 'No term list given in compose_dict_from_key()'
        return None

    vallist = key.split(separator)
    i = 0
    d = {}

    for t in termlist:
        d[t]=vallist[i]
        i += 1

    return d

def compose_key_from_row(row, terms, separator='|'):
    ''' Create a string of values of terms in a dictionary separated by separator.
    parameters:
        row -  dictionary of key:value pairs (required)
            (e.g., {'country':'United States', 'countryCode':'US'} )
        terms - string of field names for values in the row from which to construct the 
            composite key (required)
            (e.g., 'continent|country|countryCode')
        separator - string separating the values in terms (default '|')
    returns:
        values - string of separator-separated values (e.g., '|United States|US')
    '''
    if row is None or len(row)==0:
#        print 'No row given in compose_key_from_row()'
        return None

    if terms is None or len(terms)==0:
#        print 'No terms given in compose_key_from_row()'
        return None

    termlist = terms.split(separator)
    vallist=[]

    for t in termlist:
        try:
            v=row[t]
            vallist.append(v)
        except:
            vallist.append('')
    values=compose_key_from_list(vallist)

    return values

def distinct_composite_term_values_from_file(inputfile, terms, separator = '|', dialect=None):
    """Get the list of distinct composite values of set of terms in a file.
    parameters:
        inputfile - full path to the input file (required)
        terms - string containing the fields to use for the key (required)
        separator - string that separates the fieldnames in terms (default '|')
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        a list of distinct values of the composite term
    """
    if inputfile is None or len(inputfile)==0:
#        print 'No input file given in distinct_composite_term_values_from_file()'
        return None

    if os.path.isfile(inputfile) == False:
#        print 'Input file %s not found in distinct_composite_term_values_from_file()' \
#            % inputfile
        return None

    if terms is None or len(terms)==0:
#        print 'No term string given in distinct_composite_term_values_from_file()'
        return None

    if dialect is None:
        dialect = csv_file_dialect(inputfile)

    header = read_header(inputfile, dialect)
    if header is None:
#        s = 'No header found for input file %s' % inputfile
#        s += ' in distinct_composite_term_values_from_file()'
#        print '%s' % s
        return None

    termlist = terms.split(separator)

    values = set()

    # Iterate over the file rows to get the values of the terms
    with open(inputfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
        # Read the header
        dr.next()
        # Now pull out the values of all the terms in the term composite
        # for every row and add the key to the vocabulary with the values of the 
        # constituent terms.
        for row in dr:
            vallist=[]
            for t in termlist:
                try:
                    v=row[t]
                    vallist.append(v)
                except:
                    vallist.append('')
            values.add(compose_key_from_list(vallist))

    return list(values)

def distinct_term_values_from_file(inputfile, termname, dialect=None):
    """Get the list of distinct values of a term in a file.
    parameters:
        inputfile - full path to the input file (required)
        termname - field name to get distinct values of (required) 
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        a sorted list of distinct values of the term
    """
    if inputfile is None or len(inputfile)==0:
#        print 'Input file not given for distinct_term_values_from_file()'
        return None

    if os.path.isfile(inputfile) == False:
        # It's actually OK if the file does not exist. Just return None
#        print 'Input file %s not found for distinct_term_values_from_file()' % inputfile
        return None

    if termname is None or len(termname)==0:
#        print 'No term name given for distinct_term_values_from_file()'
        return None

    if dialect is None:
        dialect = csv_file_dialect(inputfile)

    header = read_header(inputfile, dialect)

    if header is None:
#        s = 'No header found for input file %s' % inputfile
#        s += ' in distinct_term_values_from_file()'
#        print '%s' % s
        return None

    if termname not in header:
#        s = 'Term %s not found in header for input file %s' % (termname, inputfile)
#        s += ' in distinct_term_values_from_file()'
#        print '%s' % s
        return None

    values = set()

    with open(inputfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
        # Read the header
        dr.next()
        for row in dr:
            values.add(row[termname])

    return sorted(list(values))

def distinct_term_counts_from_file(inputfile, termname, dialect=None):
    """Get the list of distinct values of a term and the number of times each occurs in
       the input file.
    parameters:
        inputfile - full path to the input file (required)
        termname - field name to get distinct values of (required) 
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        a list of distinct values of the term, sorted by the number of occurrences of the 
        value in descending order (most commonly found term value first).
    """
    if inputfile is None or len(inputfile)==0:
#        print 'Input file not given for distinct_term_counts_from_file()'
        return None

    if os.path.isfile(inputfile) == False:
        # It's actually OK if the file does not exist. Just return None
#        print 'Input file %s not found for distinct_term_counts_from_file()' % inputfile
        return None

    if dialect is None:
        dialect = csv_file_dialect(inputfile)

    header = read_header(inputfile, dialect)

    if header is None:
#        s = 'No header found for input file %s' % inputfile
#        s += ' in distinct_term_counts_from_file()'
#        print '%s' % s
        return None

    if termname not in header:
#        s = 'Term %s not found in header for input file %s' % (termname, inputfile)
#        s += ' in distinct_term_counts_from_file()'
#        print '%s' % s
        return None

    values = {}

    with open(inputfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=header)
        # Read the header
        dr.next()
        for row in dr:
            if row[termname] in values:
                values[row[termname]] += 1
            else:
                values[row[termname]] = 1

    return sorted(values.iteritems(), key=itemgetter(1), reverse=True)

def terms_not_in_dwc(checklist):
    """From a list of terms, get those that are not Darwin Core terms.
    parameters:
        checklist - list of values to check against Darwin Core (required)
    returns:
        a sorted list of non-Darwin Core terms from the checklist
    """
    # No need to check if checklist is given, not_in_list() does that
    return not_in_list(simpledwctermlist, checklist)

def not_in_list(targetlist, checklist):
    """Get the list of distinct values in a checklist that are not in a target list.
    parameters:
        targetlist - list to check to see if the value already exists there (required)
        checklist - list of values to check against the target list (required)
    returns:
        a sorted list of distinct new values not in the target list
    """
    if checklist is None or len(checklist)==0:
#        print 'No checklist given in not_in_list()'
        return None

    if targetlist is None or len(targetlist)==0:
#        print 'No target list given in not_in_list()'
        return sorted(checklist)

    newlist = []

    for v in checklist:
        if v not in targetlist:
            newlist.append(v)

    if '' in newlist:
        newlist.remove('')

    return sorted(newlist)

def keys_list(sourcedict):
    """Get the list of keys in a dictionary.
    parameters:
        sourcedict - dictionary to get the keys from (required)
    returns:
        an unsorted list of keys from the dictionary
    """
    if sourcedict is None or len(sourcedict)==0:
#        print 'No dictionary given in keys_list()'
        return None

    keylist = []

    for key, value in sourcedict.iteritems():
        keylist.append(key)

    return keylist

def distinct_vocabs_to_file(vocabfile, valuelist, dialect=None):
    """Add distinct new verbatim values from a valuelist to a vocabulary file.
    parameters:
        vocabfile - full path to the vocabulary file (required)
        valuelist - list of values to check for adding to the vocabulary file (required)
        dialect - a csv.dialect object with the attributes of the vocabulary file
            (default None)
    returns:
        newvaluelist - a sorted list of distinct verbatim values added to the vocabulary
            lookup file
    """
    if vocabfile is None or len(vocabfile)==0:
#        print 'No vocab file given in distinct_vocabs_to_file()'
        return None

    # No need to check if valuelist is given, not_in_list() does that

    # Get the distinct verbatim vales from the vocab file
    vocablist = distinct_term_values_from_file(vocabfile, 'verbatim', dialect)

    # Get the values not already in the vocab file
    newvaluelist = not_in_list(vocablist, valuelist)

    if newvaluelist is None or len(newvaluelist) == 0:
#        print 'No new values found for %s in distinct_vocabs_to_file()' % vocabfile
        return None

    if dialect is None:
        dialect = vocab_dialect()

    if not os.path.isfile(vocabfile):
        with open(vocabfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
            writer.writeheader()

    if os.path.isfile(vocabfile) == False:
#        print 'Vocab file %s not found for distinct_vocabs_to_filee()' % vocabfile
        return None

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
    recommendedreporttestfile = testdatapath + 'test_term_recommended_report.txt'
    termcountreporttestfile = testdatapath + 'test_term_count_report.txt'
    counttestfile = testdatapath + 'test_three_specimen_records.txt'

    def dispose(self):
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        recommendedreporttestfile = self.recommendedreporttestfile
        termcountreporttestfile = self.termcountreporttestfile
        if os.path.isfile(csvwriteheaderfile):
            os.remove(csvwriteheaderfile)
        if os.path.isfile(tsvfromcsvfile1):
            os.remove(tsvfromcsvfile1)
        if os.path.isfile(tsvfromcsvfile2):
            os.remove(tsvfromcsvfile2)
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        if os.path.isfile(recommendedreporttestfile):
            os.remove(recommendedreporttestfile)
        if os.path.isfile(termcountreporttestfile):
            os.remove(termcountreporttestfile)
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
        modelheader = geogvocabheader()
#        print 'len(header)=%s len(model)=%s\nheader:\n%s\nmodel:\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        s = 'incorrect number of fields in geog vocabulary header'
        self.assertEqual(len(header), len(modelheader), s)
        s = 'geog vocabulary header not equal to the model header'
        self.assertEqual(header, modelheader, s)

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
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        checklist = ['catalogNumber','catalognumber']
        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['catalognumber']
#        print 'notdwc: %s\nexpected: %s' % (notdwc, expectedlist)
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

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
#        print 'Putting distinct_vocabs_to_file(%s): %s' % (testvocabfile, valuelist)
        writtenlist = distinct_vocabs_to_file(testvocabfile, valuelist)
#        print 'writtenlist1: %s' % writtenlist
        # Check that the testvocabfile exists
        self.assertEqual(writtenlist, ['a', 'b', 'c'],
            'new values abc for target list not written to testvocabfile')
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for first checklist' % testvocabfile
        self.assertTrue(check, s)

        checklist = ['c', 'd', 'a', 'e']
        writtenlist = distinct_vocabs_to_file(testvocabfile, checklist)
#        print 'writtenlist2: %s' % writtenlist
        self.assertEqual(writtenlist, ['d', 'e'],
            'new values de for target list not written to testvocabfile')
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for second checklist' % testvocabfile
        self.assertTrue(check, s)

#        print 'Getting distinct_term_values_from_file(%s)' % (testvocabfile)
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
        geogkey = compose_key_from_list(geogkeytermlist)
        expected = [
            geogkey,
            'checked', 'incorrectable', 'continent', 'country', 'countryCode', 
            'stateProvince', 'county', 'municipality', 'waterBody', 'islandGroup',
            'island', 'error', 'comment', 'higherGeographyID']
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

    def test_prefix_keys(self):
        print 'testing prefix_keys'
        d = {}
        newd = prefix_keys(d)
        s = 'prefix_keys returned dict for empty input dict'
        self.assertIsNone(newd, s)
        
        thekey = 'akey'
        d = { thekey:'avalue' }
        newd = prefix_keys(d)
        s = 'prefix_keys returned dict with length different from input dict'
        self.assertEqual(len(d), len(newd), s)

        expected = d[thekey]
        s = 'expected prefixed key name (%s) not found' % expected
        try:
            found = newd['new_'+thekey]
        except:
            found = None
        self.assertIsNotNone(found, s)
        
    def test_compose_dict_from_key(self):
        print 'testing compose_dict_from_key'
        key = '|United States|US'
        termlist = ['continent', 'country', 'countryCode']

        d = compose_dict_from_key('', termlist)
        s = 'compose_dict_from_key returned dict for empty input key'
        self.assertIsNone(d, s)

        d = compose_dict_from_key(key, None)
        s = 'compose_dict_from_key returned dict for empty termlist'
        self.assertIsNone(d, s)

#        print 'key: %s\ntermlist: %s' % (key, termlist)
        d = compose_dict_from_key(key, termlist)
#        print 'd: %s' % d
        try:
            continent = d['continent']
        except:
            continent = None
        s = 'continent not in composed dictionary'
        self.assertIsNotNone(continent, s)
        s = 'continent %s not zero length' % continent
        self.assertEqual(len(continent), 0, s)

        try:
            country = d['country']
        except:
            country = None
        s = 'country not in composed dictionary'
        self.assertIsNotNone(country, s)
        expected = 'United States'
        s = 'country %s not as expected %s' % (country, expected)
        self.assertEqual(country, expected, s)

        try:
            countrycode = d['countryCode']
        except:
            countrycode = None
        s = 'countrycode not in composed dictionary'
        self.assertIsNotNone(countrycode, s)
        expected = 'US'
        s = 'countryCode %s not as expected %s' % (countrycode, expected)
        self.assertEqual(countrycode, expected, s)

    def test_compose_key_from_row(self):
        print 'testing compose_key_from_row'
        row = {'country':'United States', 'countryCode':'US'}
        terms = 'continent|country|countryCode'
        
        k = compose_key_from_row(None, terms)
        s = 'compose_key_from_row returned a key without an input row'
        self.assertIsNone(k, s)

        k = compose_key_from_row(row, '')
        s = 'compose_key_from_row returned a key without an input field list string'
        self.assertIsNone(k, s)

        k = compose_key_from_row(row, terms)
        expected = '|United States|US'
        s = 'key %s not as expected %s' % (k, expected)
        self.assertEqual(k, expected, s)

if __name__ == '__main__':
    print '=== dwca_vocab_utils.py ==='
    unittest.main()

def compose_key_from_row(row, terms, separator='|'):
    ''' Create a string of values of terms in a dictionary separated by separator.
    parameters:
        row -  dictionary of key:value pairs 
            (e.g., {'country':'United States', 'countryCode':'US'} )
        terms - string of field names for values in the row from which to construct the 
            composite key (e.g., 'continent|country|countryCode')
        separator - string separating the values in terms (default '|')
    returns:
        values - string of separator-separated values (e.g., '|United States|US')
    '''
    if row is None or len(row)==0:
        print 'No row given in compose_key_from_row()'
        return None
    if terms is None or len(terms)==0:
        print 'No terms given in compose_key_from_row()'
        return None
    termlist = terms.split(separator)
#    print 'termlist:%s\nrow:%s' % (termlist, row)
    vallist=[]
    for t in termlist:
#        print 't: %s' %t
        try:
            v=row[t]
            vallist.append(v)
        except:
            vallist.append('')
#    print 'vallist: %s' % vallist
    values=compose_key_from_list(vallist)
#    print 'values: %s' % values
    return values
