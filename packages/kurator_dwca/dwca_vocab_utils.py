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
__version__ = "dwca_vocab_utils.py 2016-09-10T13:50+02:00"

# This file contains common utility functions for dealing with the vocabulary management
# for Darwin Core-related terms
#
# Example:
#
# python dwca_vocab_utils.py

from dwca_utils import lstripstr
from dwca_utils import csv_file_dialect
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_utils import extract_values_from_file
from dwca_terms import simpledwctermlist
from dwca_terms import vocabfieldlist
from dwca_terms import vocabrowdict
from dwca_terms import controlledtermlist
from dwca_terms import geogkeytermlist
from operator import itemgetter
import os.path
import glob
import logging
import unittest
import copy
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
    return ['geogkey'] + geogkeytermlist + vocabfieldlist

def vocabheader(key, separator='|'):
    ''' Construct the header row for a vocabulary file. Begin with a field name equal to 
    the key variable, then add fields for the components of the key if it is composite 
    (i.e., it has field names separated by the separato, then add the remaining field 
    names from the standard vocabfieldlist.
    parameters:
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        fieldnames - list of fields in the vocabulary header
    Example:
      if key = 'country|stateprovince'
      and
      vocabfieldlist = ['standard', 'vetted']
      then the header will end up as 
      ['country|stateprovince','country','stateprovince','standard','vetted']
    '''
    if key is None:
        return None
    composite = key.split(separator)
    if len(composite) > 1:
        return [key] + key.split(separator) + vocabfieldlist
    return [key] + vocabfieldlist

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
        logging.debug('No vocabulary file given in writevocabheader().')
        return False

    if fieldnames is None or len(fieldnames) == 0:
        logging.debug('No list of field names given in writevocabheader().')
        return False

    if dialect is None:
        dialect = tsv_dialect()

    with open(fullpath, 'w') as outfile:
        try:
            writer = csv.DictWriter(outfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()
        except:
            logging.debug('No header written to file %s in writevocabheader()' % fullpath)
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
        logging.debug('No list given in compose_key_from_list()')
        return None

#    print 'alist: %s' % alist

    n=0
    for value in alist:
        if n==0:
            if value is None:
                return None
            key=value.strip()
            n=1
        else:
            if value is None:
                value=''
            key=key+separator+value.strip()
    return key

def vocab_dialect():
    """Get a dialect object with properties for vocabulary management files.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with TSV attributes"""
    return tsv_dialect()

def matching_vocab_dict_from_file(checklist, vocabfile, key, separator='|', dialect=None):
    """Given a checklist of values, get matching values from a vocabulary file. Values
       can match exactly, or they can match after making lower case and stripping 
       whitespace.
    parameters:
        checklist - list of values to get from the vocabfile (required)
        vocabfile - full path to the vocabulary lookup file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
        dialect - csv.dialect object with the attributes of the vocabulary lookup file 
            (default None)
    returns:
        matchingvocabdict - dictionary of complete vocabulary records matching the values 
            in the checklist
    """
    if checklist is None or len(checklist)==0:
        logging.debug('No list of values given in matching_vocab_dict_from_file()')
        return None

    vocabdict = vocab_dict_from_file(vocabfile, key, separator, dialect)
    if vocabdict is None or len(vocabdict)==0:
        logging.debug('No vocabdict constructed in matching_vocab_dict_from_file()')
        return None

#    print 'vocabdict: %s vocabfile: %s key: %s separator: %s' % \
#        (vocabdict, vocabfile, key, separator)

    matchingvocabdict = {}

    # Look through every value in the checklist
    for value in checklist:
        # If the value is in the vocabulary, get the vocabulary entry for it
        if value in vocabdict:
            matchingvocabdict[value]=vocabdict[value]
        # Otherwise try look in the vocabulary for a version of the value as lower case
        # and stripped of leading and trailing white space.
        else:
            terms = value.split(separator)
            newvalue = ''
            n=0
            for term in terms:
                if n==0:
                    newvalue = term.strip().lower()
                    n=1
                else:
                    newvalue = newvalue + separator + term.strip().lower()
            # If the simplified version of the value is in the dictionary, get the 
            # vocabulary entry for it.
            if newvalue in vocabdict:
                matchingvocabdict[value]=vocabdict[newvalue]

    return matchingvocabdict

def vetted_vocab_dict_from_file(vocabfile, key, separator='|', dialect=None):
    """Get the vetted vocabulary as a dictionary from a file.
    parameters:
        vocabfile - path to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        vocabdict - dictionary of complete vetted vocabulary records
    """
    # No need to check for vocabfile, vocab_dict_from_file does that.
    thedict = vocab_dict_from_file(vocabfile, key, separator, dialect)
    vetteddict = {}
    for entry in thedict:
        if thedict[entry]['vetted'] == '1':
            vetteddict[entry]=thedict[entry]
    return vetteddict

def vocab_dict_from_file(vocabfile, key, separator='|', dialect=None):
    """Get a vocabulary as a dictionary from a file.
    parameters:
        vocabfile - path to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
    returns:
        vocabdict - dictionary of complete vocabulary records
    """

    if key is None or len(key.strip()) == 0:
        return None

    if vocabfile is None or len(vocabfile) == 0:
        logging.debug('No vocabulary file given in vocab_dict_from_file().')
        return False

    if os.path.isfile(vocabfile) == False:
        s = 'Vocabulary file %s not found in vocab_dict_from_file().' % vocabfile
        logging.debug(s)
        return None

    if dialect is None:
        dialect = vocab_dialect()
    
    fieldnames = vocabheader(key, separator)

    vocabdict = {}

    with open(vocabfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=fieldnames)
        # Read the header
        dr.next()
        for row in dr:
            rowdict = copy.deepcopy(row)
            rowdict.pop(key)
            for f in vocabfieldlist:
                rowdict[f]=row[f]
            vocabdict[row[key]]=rowdict
#    print 'vocabdict: %s' % vocabdict
    return vocabdict

def term_values_recommended(lookupdict):
    """Get non-standard values and their standard equivalents from a lookupdict
    parameters:
        lookupdict - dictionary of lookup terms from a vocabulary (required)
    returns:
        recommended - dictionary of verbatim values and their recommended equivalents
    """
    if lookupdict is None or len(lookupdict)==0:
        logging.debug('No lookup dictionary given in term_values_recommended().')
        return None

    recommended = {}

    for key, value in lookupdict.iteritems():
        if value['vetted']=='1':
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
        logging.debug('No dictionary given in prefix_keys().')
        return None

    newd = {}

    for k in d:
        newd[prefix+k]=d[k]

    return newd

def compose_dict_from_key(key, fieldlist, separator='|'):
    ''' Create a dictionary from a string, a separator, and an ordered list of the names
        of the fields in the key.
    parameters:
        key - the field name that holds the distinct values in the vocabulary file
            (optional; default None)
        key - string from which to make the dict (required) (e.g., '|United States|US')
        fieldlist - ordered list of field names for the values in the key (required)
            (e.g., ['continent', 'country', 'countryCode'])
        separator - string separating the values in the key (default '|')
    returns:
        d - dictionary of fields and their values 
            (e.g., {'continent':'', 'country':'United States', 'countryCode':'US' } )
    '''
    if key is None or len(key)==0:
        logging.debug('No key given in compose_dict_from_key()')
        return None

    if fieldlist is None or len(fieldlist)==0:
        logging.debug('No term list given in compose_dict_from_key()')
        return None

    vallist = key.split(separator)
    i = 0
    d = {}

    for t in fieldlist:
        d[t]=vallist[i]
        i += 1

    return d

def compose_key_from_row(row, fields, separator='|'):
    ''' Create a string of values of terms in a dictionary separated by separator.
    parameters:
        row -  dictionary of key:value pairs (required)
            (e.g., {'country':'United States', 'countryCode':'US'} )
        fields - string of field names for values in the row from which to construct the 
            key (required)
            (e.g., 'continent|country|countryCode')
        separator - string separating the values in terms (default '|')
    returns:
        values - string of separator-separated values (e.g., '|United States|US')
    '''
    if row is None or len(row)==0:
        logging.debug('No row given in compose_key_from_row()')
        return None

    if fields is None or len(terms.strip())==0:
        logging.debug('No terms given in compose_key_from_row()')
        return None

    fieldlist = fields.split(separator)
    vallist=[]

    for t in fieldlist:
        try:
            v=row[t]
            vallist.append(v)
        except:
            vallist.append('')
    values=compose_key_from_list(vallist)

    return values

def terms_not_in_dwc(checklist, casesensitive=True):
    """From a list of terms, get those that are not Darwin Core terms.
    parameters:
        checklist - list of values to check against Darwin Core (required)
        casesensitive - True if the test for inclusion is case sensitive (default True)
    returns:
        a sorted list of non-Darwin Core terms from the checklist
    """
    # No need to check if checklist is given, not_in_list() does that
    if casesensitive:
        return not_in_list(simpledwctermlist, checklist)
    lowerdwc = []
    for term in simpledwctermlist:
        lowerdwc.append(term.lower())
    lowerchecklist = []
    lookup = {}
    for term in checklist:
        lterm = term.lower()
        lowerchecklist.append(lterm)
        lookup[lterm] = term
    notfound = not_in_list(lowerdwc, lowerchecklist)
    count = len(notfound)
    i = 0
    while i < count:
        notfound[i] = lookup[notfound[i]]
        i += 1
    return notfound

def terms_not_in_darwin_cloud(checklist, dwccloudfile, vetted=True):
    """Get the list of distinct values in a checklist that are not in the Darwin Cloud
       vocabulary. Verbatim values in the Darwin Cloud vocabulary should be lower-case and
       stripped already, so that is what must be matched here. The Darwin Cloud vocabulary
       should have the case-sensitive standard value.
    parameters:
        checklist - list of values to check against the target list (required)
        dwccloudfile - the vocabulary file for the Darwin Cloud (required)
        vetted - set to False if unvetted values should also be returned (default True)
    returns:
        a sorted list of distinct new values not in the Darwin Cloud vocabulary
    """
    if checklist is None or len(checklist)==0:
        logging.debug('No checklist given in terms_not_in_darwin_cloud()')
        return None
    thelist = []
    for term in checklist:
        thelist.append(term.lower())
    # No need to check if dwccloudfile is given and exists, vocab_dict_from_file() and
    # vetted_vocab_dict_from_file() do that.
    if vetted==True:
        darwinclouddict = vetted_vocab_dict_from_file(dwccloudfile, 'verbatim')
    else:
        darwinclouddict = vocab_dict_from_file(dwccloudfile, 'verbatim')
    darwincloudlist = []
    for term in darwinclouddict:
        darwincloudlist.append(term)
    return not_in_list(darwincloudlist, thelist)

def darwinize_list(termlist, dwccloudfile):
    """Translate the terms in a list to standard Darwin Core terms.
    parameters:
        termlist - list of values to translate (required)
        dwccloudfile - the vocabulary file for the Darwin Cloud (required)
    returns:
        a list with all translatable terms translated
    """
    if termlist is None or len(termlist)==0:
        logging.debug('No termlist given in darwinize_list()')
        return None
    # No need to check if dwccloudfile is given and exists, vetted_vocab_dict_from_file() 
    # does that.
    darwinclouddict = vetted_vocab_dict_from_file(dwccloudfile, 'verbatim')
    if darwinclouddict is None:
        logging.debug('No Darwin Cloud terms in darwinize_list()')
        return None
    thelist = []
    for term in termlist:
        thelist.append(term.lower().strip())
#    print 'dwccloudfile: %s' % dwccloudfile
#    print 'thelist: %s' % thelist
#    print 'darwinclouddict: %s' % darwinclouddict
    darwinizedlist = []
    i = 0
    j = 1
    for term in thelist:
        if term in darwinclouddict and len(darwinclouddict[term]['standard'].strip()) > 0:
            newterm = darwinclouddict[term]['standard']
#            print 'term: %s newterm: %s' % (term, newterm)
        else:
            newterm = termlist[i].strip()
            if len(newterm) == 0:
                newterm = 'unnamedcolumn_%s' % j
                j += 1
        darwinizedlist.append(newterm)
        i += 1
    return darwinizedlist

def not_in_list(targetlist, checklist):
    """Get the list of distinct values in a checklist that are not in a target list.
    parameters:
        targetlist - list to check to see if the value already exists there (required)
        checklist - list of values to check against the target list (required)
    returns:
        a sorted list of distinct new values not in the target list
    """
    if checklist is None or len(checklist)==0:
        logging.debug('No checklist given in not_in_list()')
        return None

    if targetlist is None or len(targetlist)==0:
        logging.debug('No target list given in not_in_list()')
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
        logging.debug('No dictionary given in keys_list()')
        return None

    keylist = []

    for key, value in sourcedict.iteritems():
        keylist.append(key)

    return keylist

def distinct_vocabs_to_file(vocabfile, valuelist, key, separator='|', dialect=None):
    """Add distinct new verbatim values from a valuelist to a vocabulary file.
    parameters:
        vocabfile - full path to the vocabulary file (required)
        valuelist - list of values to check for adding to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
        dialect - a csv.dialect object with the attributes of the vocabulary file
            (default None)
    returns:
        newvaluelist - a sorted list of distinct verbatim values added to the vocabulary
            lookup file
    """
    # print '%s distinct_vocabs_to_file()' % __version__
    # print 'vocabfile: %s' % vocabfile
    # print 'valuelist: %s' % valuelist
    # print 'key: %s' % key
    # print 'separator: %s' % separator

    if vocabfile is None or len(vocabfile.strip())==0:
        logging.debug('No vocab file given in distinct_vocabs_to_file()')
        return None

    # No need to check if valuelist is given, not_in_list() does that

    # Get the distinct verbatim values from the vocab file
    vocablist = extract_values_from_file(vocabfile, [key], separator='|')

    # print 'vocablist: %s' % vocablist

    # Get the values not already in the vocab file
    newvaluelist = not_in_list(vocablist, valuelist)

    # print 'newvalueslist: %s' % newvaluelist

    if newvaluelist is None or len(newvaluelist) == 0:
        s = 'No new values found for %s in distinct_vocabs_to_file()' % vocabfile
        logging.debug(s)
        return None

    if dialect is None:
        dialect = vocab_dialect()

    fieldnames = vocabheader(key, separator)

    # print 'fieldnames: %s' % fieldnames

    if not os.path.isfile(vocabfile):
        with open(vocabfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
            writer.writeheader()

    if os.path.isfile(vocabfile) == False:
        s = 'Vocab file %s not found for distinct_vocabs_to_file()' % vocabfile
        logging.debug(s)
        return None

    foundheader = read_header(vocabfile)
    
    # print 'foundheader: %s' % foundheader

    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        for term in newvaluelist:
            row = copy.deepcopy(vocabrowdict)
            row[key] = term
            # print 'row out: %s' % row
            writer.writerow(row)

    return newvaluelist

def compose_key_from_row(row, fields, separator='|'):
    ''' Create a string of values of fields in a dictionary separated by separator.
    parameters:
        row -  dictionary of key:value pairs 
            (e.g., {'country':'United States', 'countryCode':'US'} )
        fields - string of field names for values in the row from which to construct the 
            key (e.g., 'continent|country|countryCode')
        separator - string separating the values in fields (default '|')
    returns:
        values - string of separator-separated values (e.g., '|United States|US')
    '''
    if row is None or len(row)==0:
        s = 'No row given in compose_key_from_row()'
        logging.debug(s)
        return None
    if fields is None or len(fields)==0:
        s = 'No terms given in compose_key_from_row()'
        logging.debug(s)
        return None
    fieldlist = fields.split(separator)
    vallist=[]
    for t in fieldlist:
        try:
            v=row[t]
            vallist.append(v)
        except:
            vallist.append('')
    values=compose_key_from_list(vallist)
    return values

class DWCAVocabUtilsFramework():
    # testdatapath is the location of example files to test with
    testdatapath = './data/tests/'
    # vocabpath is the location of vocabulary files to test with
    vocabpath = './data/vocabularies/'

    # following are files used as input during the tests, don't remove these
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    monthvocabfile = testdatapath + 'test_vocab_month.txt'
    geogvocabfile = vocabpath + 'dwc_geography.txt'
    darwincloudfile = vocabpath + 'dwc_cloud.txt'

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
        if os.path.isfile(recommendedreporttestfile):
            os.remove(recommendedreporttestfile)
        if os.path.isfile(termcountreporttestfile):
            os.remove(termcountreporttestfile)
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
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
            expected = [field.lower()] + vocabfieldlist
            s = 'File: %s\nheader: %s\n' % (vocabfile, header)
            s += 'not as expected: %s' % expected
            self.assertEqual(header, expected, s)

    def test_read_vocab_header(self):
        print 'testing read_vocab_header'
        dialect = vocab_dialect()
        monthvocabfile = self.framework.monthvocabfile
        header = read_header(monthvocabfile, dialect)
#        print 'len(header)=%s len(model)=%s\nheader:\n%s\nmodel:\n%s' \
#            % (len(header), len(vocabfieldlist), header, vocabfieldlist)
        self.assertEqual(len(header), 8, 'incorrect number of fields in header')

        expected = ['month'] + vocabfieldlist
        s = 'File: %s\nheader: %s\n' % (monthvocabfile, header)
        s += 'not as expected: %s' % expected
        self.assertEqual(header, expected, s)

    def test_read_geog_header(self):
        print 'testing read_geog_header'
        dialect = vocab_dialect()
        geogvocabfile = self.framework.geogvocabfile
        header = read_header(geogvocabfile, dialect)
        expected = geogvocabheader()

        s = 'File: %s\nheader: %s\n' % (geogvocabfile, header)
        s += 'not as expected: %s' % expected
        self.assertEqual(header, expected, s)

    def test_vocab_dict_from_file(self):
        print 'testing vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        monthdict = vocab_dict_from_file(monthvocabfile, 'month')
        expected = 8
#        print 'monthdict:\n%s' % monthdict
#        s = 'month vocab at %s has %s items in it instead of %s' % \
#            (monthvocabfile, len(monthdict), expected)
#        self.assertEqual(len(monthdict), expected, s)

        seek = 'vi'
        s = "%s not found in month dictionary:\n%s" % (seek, monthdict)
        self.assertTrue('vi' in monthdict, s)
        field = 'comment'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'vetted'
        expected = '0'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'standard'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'unresolved'
        expected = '0'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'source'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'error'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'misplaced'
        expected = '0'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)

        seek = '5'
        s = "%s not found in month dictionary:\n%s" % (seek, monthdict)
        self.assertTrue(seek in monthdict, s)
        field = 'comment'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'vetted'
        expected = '1'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'standard'
        expected = '5'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'unresolved'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'source'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'error'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'misplaced'
        expected = ''
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)

    def test_matching_vocab_dict_from_file(self):
        print 'testing vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        checklist = ['vi', '5', 'fdsf']
        monthdict = matching_vocab_dict_from_file(checklist, monthvocabfile, 'month')
#        print 'matchingmonthdict:\n%s' % monthdict
        s = 'month vocab at %s does has %s matching items in it instead of 2' % \
            (monthvocabfile, len(monthdict))
        self.assertEqual(len(monthdict), 2, s)

        self.assertTrue('vi' in monthdict,"'vi' not found in month dictionary")
        self.assertEqual(monthdict['vi']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['vetted'], '0', 
            "value of 'vetted' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['standard'], '', 
            "value of 'standard' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['unresolved'], '0', 
            "value of 'unresolved' not equal to 0 for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['source'], '', 
            "value of 'source' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['error'], '', 
            "value of 'error' not equal to '' for vocab value 'vi'")
        self.assertEqual(monthdict['vi']['misplaced'], '0', 
            "value of 'misplaced' not equal to '0' for vocab value 'vi'")

        self.assertTrue('5' in monthdict,"'5' not found in month dictionary")
        self.assertEqual(monthdict['5']['comment'], '', 
            "value of 'comment' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['vetted'], '1', 
            "value of 'vetted' not equal to 1 for vocab value '5'")
        self.assertEqual(monthdict['5']['standard'], '5', 
            "value of 'standard' not equal to '5' for vocab value '5'")
        self.assertEqual(monthdict['5']['unresolved'], '', 
            "value of 'unresolved' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['source'], '', 
            "value of 'source' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['error'], '', 
            "value of 'error' not equal to '' for vocab value '5'")
        self.assertEqual(monthdict['5']['misplaced'], '', 
            "value of 'misplaced' not equal to '' for vocab value '5'")

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

        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['catalognumber']
#        print 'notdwc: %s\nexpected: %s' % (notdwc, expectedlist)
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

    def test_terms_not_in_darwin_cloud(self):
        print 'testing terms_not_in_darwin_cloud'
        checklist = ['stuff', 'nonsense', 'Year']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = terms_not_in_darwin_cloud(checklist, darwincloudfile)
        expectedlist = ['nonsense', 'stuff']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

    def test_darwinize_list(self):
        print 'testing darwinize_list'
        checklist = ['STUFF', 'Nonsense', 'Year', '  ', 'dwc:day', 'MONTH ', \
            'lifestage', 'Id']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = darwinize_list(checklist, darwincloudfile)
        expectedlist = ['STUFF', 'Nonsense', 'year', 'unnamedcolumn_1', 'day', 'month', \
            'lifeStage', 'Id']
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
        writtenlist = distinct_vocabs_to_file(testvocabfile, valuelist, 'verbatim')
        expected = ['a', 'b', 'c']
#        print 'writtenlist1: %s' % writtenlist
        # Check that the testvocabfile exists
        s = 'writtenlist: %s not as expected: %s' % (writtenlist, expected)
        self.assertEqual(writtenlist, expected, s)
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for first checklist' % testvocabfile
        self.assertTrue(check, s)

        fulllist = extract_values_from_file(testvocabfile, ['verbatim'])
#        print 'fulllist: %s' % fulllist
        
        checklist = ['c', 'd', 'a', 'e']
        writtenlist = distinct_vocabs_to_file(testvocabfile, checklist, 'verbatim')
        expected = ['d', 'e']
#        print 'writtenlist2: %s' % writtenlist
        s = 'writtenlist: %s not as expected: %s' % (writtenlist, expected)
        self.assertEqual(writtenlist, expected, s)
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for second checklist' % testvocabfile
        self.assertTrue(check, s)

        fulllist = extract_values_from_file(testvocabfile, ['verbatim'])
        expected = ['a', 'b', 'c', 'd', 'e']
        s = 'Extracted values: %s\n not as expected: %s' % (fulllist, expected)
#        print 'fulllist: %s' % fulllist
        self.assertEqual(fulllist, expected, s)

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

    def test_vocabheader(self):
        print 'testing vocabheader'
        # Example:
        # if keyfields = 'country|stateprovince|county'
        # and
        # vocabfieldlist = ['standard','vetted']
        # then the header will end up as 
        # 'country|stateprovince|county, country, stateprovince, county, standard, vetted'
        keyfields = 'country|stateprovince|county'
        header = vocabheader(keyfields)
#        print 'vocabheader:\n%s' % header
        expected = ['country|stateprovince|county', 'country', 'stateprovince', 
            'county', 'standard', 'vetted', 'error', 'misplaced', 'unresolved', 'source', 
            'comment']
        s = 'header:\n%s\nnot as expected:\n%s' % (header,expected)
        self.assertEqual(header, expected, s)

    def test_writevocabheader(self):
        print 'testing writevocabheader'
        writevocabheadertestfile = self.framework.writevocabheadertestfile
        fieldnames = ['country|stateprovince|county', 'standard', 'vetted', 'error', 
            'misplaced', 'unresolved', 'source', 'comment']
        dialect = vocab_dialect()
        success = writevocabheader(writevocabheadertestfile, fieldnames, dialect)
        self.assertTrue(success,'vocab header not written')
        
        header = read_header(writevocabheadertestfile)
        expected = ['country|stateprovince|county', 'standard', 'vetted', 'error', 
            'misplaced', 'unresolved', 'source', 'comment']
        s = 'header:\n%s\nfrom file: %s\nnot as expected:\n%s' \
            % (header,writevocabheadertestfile,expected)
        self.assertEqual(header, expected, s)

    def test_geogvocabheader(self):
        print 'testing geogvocabheader'
        header = geogvocabheader()
#        geogkey = compose_key_from_list(geogkeytermlist)
        expected = [
            'geogkey', 'continent', 'country', 'countryCode', 'stateProvince', 'county', 
            'municipality', 'waterBody', 'islandGroup', 'island', 'standard', 'vetted', 
            'error', 'misplaced', 'unresolved', 'source', 'comment']
        s = 'geog header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_term_values_recommended(self):
        print 'testing term_values_recommended'
        monthvocabfile = self.framework.monthvocabfile
        monthdict = vocab_dict_from_file(monthvocabfile, 'month')
        recommended = term_values_recommended(monthdict)
#        print 'monthdict:\n%s\nrecommended:\n%s' % (monthdict, recommended)
        expected = {
            'v': {'comment': '', 'vetted': '1', 'standard': '5', 
                'unresolved': '', 'source': '', 'error': '', 'misplaced': ''},
            'V': {'comment': '', 'vetted': '1', 'standard': '5', 
                'unresolved': '', 'source': '', 'error': '', 'misplaced': ''} 
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
