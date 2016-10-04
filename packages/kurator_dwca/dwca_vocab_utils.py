#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__version__ = "dwca_vocab_utils.py 2016-10-04T14:58+02:00"

# This file contains common utility functions for dealing with the vocabulary management
# for Darwin Core-related terms
#
# Example:
#
# python dwca_vocab_utils.py

from dwca_utils import ustripstr
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import clean_header
from dwca_utils import tsv_dialect
from dwca_utils import csv_dialect
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import read_csv_row
from dwca_utils import extract_values_from_file
from dwca_utils import setup_actor_logging
from dwca_utils import utf8_data_encoder
from dwca_terms import simpledwctermlist
from dwca_terms import vocabfieldlist
from dwca_terms import vocabrowdict
from dwca_terms import controlledtermlist
from dwca_terms import geogkeytermlist
from dwca_terms import geogvocabaddedfieldlist
import os.path
import logging
import unittest
import copy

# Replace the system csv with unicodecsv. All invocations of csv will use unicodecsv,
# which supports reading and writing unicode streams.
try:
    import unicodecsv as csv
except ImportError:
    import warnings
    s = "The unicodecsv package is required.\n"
    s += "pip install unicodecsv\n"
    s += "jython pip install unicodecsv"
    warnings.warn(s)

def geogvocabheader():
    ''' Construct a header row for the geog vocabulary.
    parameters:
        None
    returns:
        fieldnames -  a list of field names in the header
    '''
    geogkey = compose_key_from_list(geogkeytermlist)
    return ['geogkey'] + geogkeytermlist + vocabfieldlist + geogvocabaddedfieldlist

def vocabheader(key, separator=None):
    ''' Construct the header row for a vocabulary file. Begin with a field name equal to 
    the key variable, then add fields for the components of the key if it is composite 
    (i.e., it has field names separated by the separato, then add the remaining field 
    names from the standard vocabfieldlist.
    parameters:
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
    returns:
        fieldnames - list of fields in the vocabulary header
    Example:
      if key = 'country|stateprovince' 
      and separator =  '|'
      and vocabfieldlist = ['standard', 'vetted']
      then the header will end up as 
      ['country|stateprovince','country','stateprovince','standard','vetted']
    '''
    if key is None:
        return None
    if separator is not None:
        composite = key.split(separator)
        if len(composite) > 1:
            return [key] + composite + vocabfieldlist
    return [key] + vocabfieldlist

def writevocabheader(fullpath, fieldnames, dialect=None):
    ''' Write a vocabulary header to a file in utf-8 using the chosen dialect.
    parameters:
        fullpath - the full path to the file to write into (required)
        fieldnames - list of field names in the header (required)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file 
            (default None)
    returns:
        success - True if the header was written to the file, otherwise False
    '''
    functionname = 'writevocabheader()'

    if fullpath is None or len(fullpath) == 0:
        s = 'No vocabulary file given in %s.' % functionname
        logging.debug(s)
        return False

    if fieldnames is None or len(fieldnames) == 0:
        s = 'No list of field names given in %s.' % functionname
        logging.debug(s)
        return False

    if dialect is None:
        dialect = tsv_dialect()

    success = write_header(fullpath, fieldnames, dialect)
    if success == False:
        s = 'No header written to file %s in %s.' % (fullpath, functionname)
        logging.debug(s)
        return False

    s = 'Header written to %s in %s.' % (fullpath, functionname)
    logging.debug(s)
    return True

def compose_key_from_list(alist, separator=None):
    ''' Get a string consisting of the values in a list, separated by separator.
    parameters:
        alist - list of values to compose into a string. The values cannot contain 
            the separator string (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
    returns:
        key - composed string with values separated by separator
    '''
    functionname = 'compose_key_from_list()'

    if alist is None or len(alist)==0:
        s = 'No list given in %s.' % functionname
        logging.debug(s)
        return None

    n=0
    if separator is None:
        separator = ''
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
    ''' Get a dialect object with properties for vocabulary management files.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with TSV attributes
    '''
    return tsv_dialect()

def matching_vocab_dict_from_file(
    checklist, vocabfile, key, separator=None, dialect=None, encoding=None):
    ''' Given a checklist of values, get matching values from a vocabulary file. Values
       can match exactly, or they can match after making them upper case and stripping 
       whitespace.
    parameters:
        checklist - list of values to get from the vocabfile (required)
        vocabfile - full path to the vocabulary lookup file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file 
            (default None)
        encoding - a string designating the input file encoding (optional; default None) 
            (e.g., 'utf-8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        matchingvocabdict - dictionary of complete vocabulary records matching the values 
            in the checklist
    '''
    functionname = 'matching_vocab_dict_from_file()'

    if checklist is None or len(checklist)==0:
        s = 'No list of values given in %s.' % functionname
        logging.debug(s)
        return None

    #print 'checklist: %s' % checklist

    vocabdict = vocab_dict_from_file(vocabfile, key, separator, dialect, encoding)
    if vocabdict is None or len(vocabdict)==0:
        s = 'No vocabdict constructed in %s' % functionname
        logging.debug(s)
        return None

    #print 'vocabdict: %s' % vocabdict

    matchingvocabdict = {}

    # Look through every value in the checklist
    for value in checklist:
        if separator is None:
            terms = [value]
        else:
            try:
                terms = value.split(separator)
            except Exception , e:
                s = 'Exception splitting value: %s Exception: %s ' % (value, e)
                s += 'in %s' % functionname
                logging.debug(s)
                terms = [value] # cop out
        newvalue = ''
        n=0
        for term in terms:
            if n==0:
                newvalue = ustripstr(term)
                n=1
            else:
                newvalue = newvalue + separator + ustripstr(term)

        # If the simplified version of the value is in the dictionary, get the 
        # vocabulary entry for it.
        if value in vocabdict or newvalue in vocabdict:
            matchingvocabdict[value]=vocabdict[newvalue]

    return matchingvocabdict

def missing_vocab_list_from_file(checklist, vocabfile, key, separator=None, dialect=None,
    encoding=None):
    ''' Given a checklist of values, get values not found in the given vocabulary file. 
       Values can match exactly, or they can match after making them upper case and 
       stripping whitespace.
    parameters:
        checklist - list of values to get from the vocabfile (required)
        vocabfile - full path to the vocabulary lookup file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file 
            (default None)
        encoding - a string designating the input file encoding (optional; default None) 
            (e.g., 'utf-8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        missingvocabdict - values in the checklist not found in the vocabulary file
    '''
    functionname = 'missing_vocab_list_from_file()'

    if checklist is None or len(checklist)==0:
        s = 'No list of values given in %s.' % functionname
        logging.debug(s)
        return None

    vocabdict = vocab_dict_from_file(vocabfile, key, separator, dialect, encoding)
    if vocabdict is None or len(vocabdict)==0:
        s = 'No vocabdict constructed in %s.' % functionname
        logging.debug(s)
        return None

    missingvocabset = set()

    # Look through every value in the checklist
    for value in checklist:
        if separator is None:
            terms = [value]
        else:
            try:
                terms = value.split(separator)
            except Exception , e:
                s = 'Exception splitting value: %s Exception: %s ' % (value, e)
                s += 'in %s' % functionname
                logging.debug(s)
                terms = [value] # cop out
        newvalue = ''
        n=0
        for term in terms:
            if n==0:
                newvalue = ustripstr(term)
                n=1
            else:
                newvalue = newvalue + separator + ustripstr(term)
        # If value or newvalue is in the vocabulary, nevermind
        if value in vocabdict or newvalue in vocabdict:
            pass
        # Otherwise, add the upper case, stripped value to the list
        else:
            missingvocabset.add(newvalue)

    return sorted(list(missingvocabset))

def vetted_vocab_dict_from_file(vocabfile, key, separator=None, dialect=None, 
    encoding=None):
    ''' Get the vetted vocabulary as a dictionary from a file.
    parameters:
        vocabfile - path to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
            (default None)
        encoding - a string designating the input file encoding (optional; default None) 
            (e.g., 'utf-8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        vocabdict - dictionary of complete vetted vocabulary records
    '''
    # No need to check for vocabfile, vocab_dict_from_file does that.
    thedict = vocab_dict_from_file(vocabfile, key, separator, dialect, encoding)
    vetteddict = {}
    for entry in thedict:
        if thedict[entry]['vetted'] == '1':
            vetteddict[entry]=thedict[entry]
    return vetteddict

def vocab_dict_from_file(
    vocabfile, key, separator=None, dialect=None, encoding=None, 
    function=None, *args, **kwargs):
    ''' Get a vocabulary as a dictionary from a file.
    parameters:
        vocabfile - path to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
        dialect - a csv.dialect object with the attributes of the vocabulary file
            (default None)
        encoding - a string designating the input file encoding (optional; default None) 
            (e.g., 'utf-8', 'mac_roman', 'latin_1', 'cp1252')
        function - function to call for each value to compare (default None)
        args - unnamed parameters to function as tuple (optional)
        kwargs - named parameters to function as dictionary (optional)
    Example:
       vocab_dict_from_file(v,k,function=ustripstr) would return all of the stripped, 
       uppercased keys and their values from the vocabfile v.
    returns:
        vocabdict - dictionary of complete vocabulary records
    '''
    functionname = 'vocab_dict_from_file()'

    if key is None or len(key.strip()) == 0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return None

    if vocabfile is None or len(vocabfile) == 0:
        s = 'No vocabulary file given in %s.' % functionname
        logging.debug(s)
        return None

    if os.path.isfile(vocabfile) == False:
        s = 'Vocabulary file %s not found in %s.' % (vocabfile, functionname)
        logging.debug(s)
        return None

    if dialect is None:
        dialect = vocab_dialect()
    
    # Try to determine the encoding of the inputfile.
    if encoding is None or len(encoding.strip()) == 0:
        encoding = csv_file_encoding(vocabfile)
        # csv_file_encoding() always returns an encoding if there is an input file.    

    # Set up the field names to match the standard vocabulary header
    fieldnames = vocabheader(key, separator)

    # Create a dictionary to hold the vocabulary
    vocabdict = {}

    # Iterate through all rows in the input file
    for row in read_csv_row(vocabfile, dialect, encoding, header=True, 
            fieldnames=fieldnames):
        # Make a complete copy of the row
        rowdict = copy.deepcopy(row)
        value = row[key]
        # Remove the key from the row copy
        rowdict.pop(key)
        newvalue = value
        # If we are not supposed to apply a function to the key value
        if function is not None:
            newvalue = function(value, *args, **kwargs)
        vocabdict[newvalue]=rowdict
                
    return vocabdict

def term_values_recommended(lookupdict):
    ''' Get non-standard values and their standard equivalents from a lookupdict
    parameters:
        lookupdict - dictionary of lookup terms from a vocabulary (required)
    returns:
        recommended - dictionary of verbatim values and their recommended equivalents
    '''
    functionname = 'term_values_recommended()'

    if lookupdict is None or len(lookupdict)==0:
        s = 'No lookup dictionary given in %s.' % functionname
        logging.debug(s)
        return None

    recommended = {}

    for key, value in lookupdict.iteritems():
        if value['vetted']=='1':
            if value['standard'] != key:
                recommended[key] = value

    return recommended

def recommended_value(lookupdict, lookupvalue):
    ''' Get recommended standard value for lookupvalue from a lookup dictionary
    parameters:
        lookupdict - dictionary of lookup terms from a vocabulary. Dictionary must
            contain a key for which the value is another dictionary, and that 
            subdictionary must contain a key 'standard' for which the value is the 
            recommended value. The subdictionary may contain other keys as desired 
            (required)
    returns:
        subdictionary - dictionary containing the recommended value
    '''
    functionname = 'recommended_value()'

    if lookupdict is None or len(lookupdict)==0:
        s = 'No lookup dictionary given in %s.' % functionname
        logging.debug(s)
        return None

    if lookupvalue is None or len(lookupvalue)==0:
        s = 'No lookup value given in %s.' % functionname
        logging.debug()
        return None

    try:
        subdictionary = lookupdict[lookupvalue]
        return subdictionary
    except:
        s = '"%s" not found in lookup dictionary in %s.' % (lookupvalue, functionname)
        logging.debug(s)
        return None

def compose_dict_from_key(key, fieldlist, separator=None):
    ''' Create a dictionary from a string, a separator, and an ordered list of the names
        of the fields in the key.
    parameters:
        key - the field name that holds the distinct values in the vocabulary file
            (optional; default None)
        key - string from which to make the dict (required) (e.g., '|United States|US')
        fieldlist - ordered list of field names for the values in the key (required)
            (e.g., ['continent', 'country', 'countryCode'])
        separator - string separating the values in the key (optional; default None)
    returns:
        d - dictionary of fields and their values 
            (e.g., {'continent':'', 'country':'United States', 'countryCode':'US' } )
    '''
    functionname = 'compose_dict_from_key()'

    if key is None or len(key)==0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return None

    if fieldlist is None or len(fieldlist)==0:
        s = 'No term list given in %s.' % functionname
        logging.debug(s)
        return None

    if separator is None:
        vallist = key
    else:
        vallist = key.split(separator)
    i = 0
    d = {}

    for t in fieldlist:
        d[t]=vallist[i]
        i += 1

    return d

def terms_not_in_dwc(checklist, casesensitive=False):
    ''' From a list of terms, get those that are not Darwin Core terms.
    parameters:
        checklist - list of values to check against Darwin Core (required)
        casesensitive - True if the test for inclusion is case sensitive (default True)
    returns:
        a sorted list of non-Darwin Core terms from the checklist
    '''
    # No need to check if checklist is given, not_in_list() does that
    if casesensitive==True:
        return not_in_list(simpledwctermlist, checklist)

    lowerdwc = []
    for term in simpledwctermlist:
        lowerdwc.append(ustripstr(term))

    notfound = not_in_list(lowerdwc,checklist,function=ustripstr)
    return notfound

def terms_not_in_darwin_cloud(checklist, dwccloudfile, vetted=True, casesensitive=False):
    ''' Get the list of distinct values in a checklist that are not in the Darwin Cloud
        vocabulary. Verbatim values in the Darwin Cloud vocabulary should be lower-case and
        stripped already, so that is what must be matched here. The Darwin Cloud vocabulary
        should have the case-sensitive standard value.
    parameters:
        checklist - list of values to check against the target list (required)
        dwccloudfile - the vocabulary file for the Darwin Cloud (required)
        vetted - set to False if unvetted values should also be returned (default True)
    returns:
        a sorted list of distinct new values not in the Darwin Cloud vocabulary
    '''
    functionname = 'terms_not_in_darwin_cloud()'

    if checklist is None or len(checklist)==0:
        s = 'No checklist given in %s.' % functionname
        logging.debug(s)
        return None

    # No need to check if dwccloudfile is given and exists, vocab_dict_from_file() and
    # vetted_vocab_dict_from_file() do that.
    if vetted==True:
        darwinclouddict = vetted_vocab_dict_from_file(dwccloudfile, 'fieldname')
    else:
        darwinclouddict = vocab_dict_from_file(dwccloudfile, 'fieldname')

    dwcloudlist = []
    for key, value in darwinclouddict.iteritems():
        dwcloudlist.append(key)

    if casesensitive==True:
        return not_in_list(dwcloudlist, checklist)

    lowerdwclist = []
    for term in dwcloudlist:
        lowerdwclist.append(ustripstr(term))

    notfound = not_in_list(lowerdwclist, checklist, function=ustripstr)

    return notfound

def darwinize_list(termlist, dwccloudfile):
    ''' Translate the terms in a list to standard Darwin Core terms.
    parameters:
        termlist - list of values to translate (required)
        dwccloudfile - the vocabulary file for the Darwin Cloud (required)
    returns:
        a list with all translatable terms translated
    '''
    functionname = 'darwinize_list()'

    if termlist is None or len(termlist)==0:
        s = 'No termlist given in %s.' % functionname
        logging.debug(s)
        return None

    # No need to check if dwccloudfile is given and exists, vetted_vocab_dict_from_file() 
    # does that.
    darwinclouddict = vetted_vocab_dict_from_file(dwccloudfile, 'fieldname')

    if darwinclouddict is None:
        s = 'No Darwin Cloud terms in %s.' % functionname
        logging.debug(s)
        return None

    thelist = []
    for term in termlist:
        thelist.append(ustripstr(term))

    darwinizedlist = []
    i = 0
    j = 1
    for term in thelist:
        if term in darwinclouddict:
            if darwinclouddict[term]['standard'] is not None and \
                len(darwinclouddict[term]['standard'].strip()) > 0:
                newterm = darwinclouddict[term]['standard']
            else:
                newterm = termlist[i].strip()
        else:
            newterm = termlist[i].strip()
            if len(newterm) == 0:
                newterm = 'UNNAMED_COLUMN_%s' % j
                j += 1
        darwinizedlist.append(newterm)
        i += 1

    return darwinizedlist

def not_in_list(targetlist, checklist, function=None, *args, **kwargs):
    ''' Get the list of distinct values in a checklist that are not in a target list.
        Optionally pass a function to use on the items in the checklist before determining
        equality.
    Example:
       not_in_list(a,b,function=ustripstr) would return all of the stripped, uppercased
       items in b that are not in a. The items in a do not have the function applied.
    parameters:
        targetlist - list to check to see if the value already exists there (required)
        checklist - list of values to check against the target list (required)
        function - function to call for each value to compare (default None)
        args - unnamed parameters to function as tuple (optional)
        kwargs - named parameters to function as dictionary (optional)
    returns:
        a sorted list of distinct new values not in the target list
    '''
    functionname = 'not_in_list()'

    if checklist is None or len(checklist)==0:
        s = 'No checklist given in %s.' % functionname
        logging.debug(s)
        return None

    if targetlist is None or len(targetlist)==0:
        s = 'No target list given in %s.' % functionname
        logging.debug(s)
        return sorted(checklist)

    newlist = []

    if function is None:
        for v in checklist:
            if v not in targetlist:
                newlist.append(v)
    else:
        for v in checklist:
            try:
                newvalue = function(v, *args, **kwargs)
            except:
                newvalue = v
            if newvalue not in targetlist:
                newlist.append(newvalue)

    if '' in newlist:
        newlist.remove('')

    return sorted(newlist)

def keys_list(sourcedict):
    ''' Get the list of keys in a dictionary.
    parameters:
        sourcedict - dictionary to get the keys from (required)
    returns:
        an unsorted list of keys from the dictionary
    '''
    functionname = 'keys_list()'

    if sourcedict is None or len(sourcedict)==0:
        s = 'No dictionary given in %s.' % functionname
        logging.debug(s)
        return None

    keylist = []

    for key, value in sourcedict.iteritems():
        keylist.append(key)

    return keylist

def distinct_vocabs_to_file(vocabfile, valuelist, key, separator=None, dialect=None,
    encoding=None):
    ''' Add distinct new verbatim values from a valuelist to a vocabulary file.
    parameters:
        vocabfile - full path to the vocabulary file (required)
        valuelist - list of values to check for adding to the vocabulary file (required)
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
        dialect - a csv.dialect object with the attributes of the vocabulary file
            (default None)
        encoding - a string designating the input file encoding (optional; default None) 
            (e.g., 'utf-8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        newvaluelist - a sorted list of distinct verbatim values added to the vocabulary
            lookup file
    '''
    functionname = 'distinct_vocabs_to_file()'
    
    if vocabfile is None or len(vocabfile.strip())==0:
        s = 'No vocab file given in %s.' % functionname
        logging.debug(s)
        return None

    # Determine the dialect of the input file
    if dialect is None:
        dialect = csv_file_dialect(vocabfile)
        # csv_file_dialect() always returns a dialect if there is an input file.
        # No need to check.

    # Try to determine the encoding of the inputfile.
    if encoding is None or len(encoding.strip()) == 0:
        encoding = csv_file_encoding(vocabfile)
        # csv_file_encoding() always returns an encoding if there is an input file.    

    # No need to check if valuelist is given, not_in_list() does that
    # Get the distinct verbatim values from the vocab file
    vocablist = extract_values_from_file(vocabfile, [key], separator=separator, 
        dialect=dialect, encoding=encoding)

    # Get the values not already in the vocab file
    newvaluelist = not_in_list(vocablist, valuelist)

    if newvaluelist is None or len(newvaluelist) == 0:
        s = 'No new values found for %s in %s' % (vocabfile, functionname)
        logging.debug(s)
        return None

    if dialect is None:
        dialect = vocab_dialect()

    fieldnames = vocabheader(key, separator)

    if not os.path.isfile(vocabfile):
        write_header(vocabfile, fieldnames, vocab_dialect())

    if os.path.isfile(vocabfile) == False:
        s = 'Vocab file %s not found in %s.' % (vocabfile, functionname)
        logging.debug(s)
        return None

    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        for term in newvaluelist:
            row = copy.deepcopy(vocabrowdict)
            row[key] = term
            writer.writerow(row)

    s = 'Vocabulary file written to %s in %s.' % (vocabfile, functionname)
    logging.debug(s)
    return newvaluelist

def compose_key_from_row(row, fields, separator=None):
    ''' Create a string of values of terms in a dictionary separated by separator.
    parameters:
        row -  dictionary of key:value pairs (required)
            (e.g., {'country':'United States', 'countryCode':'US'} )
        fields - string of field names for values in the row from which to construct the 
            key (required)
            (e.g., 'continent|country|countryCode')
        separator - string separating the values in fields (optional; default None)
    returns:
        values - string of separator-separated values (e.g., '|United States|US')
    '''
    functionname = 'compose_key_from_row()'

    if row is None or len(row)==0:
        s = 'No row given in %s.' % functionname
        logging.debug(s)
        return None

    if fields is None or len(fields.strip())==0:
        s = 'No terms given in %s.' % functionname
        logging.debug(s)
        return None

    if separator is None:
        fieldlist = [fields]
    else:
        fieldlist = fields.split(separator)

    vallist=[]
    for t in fieldlist:
        try:
            v=row[t]
            vallist.append(v)
        except:
            vallist.append('')
    values=compose_key_from_list(vallist, separator)

    return values

class DWCAVocabUtilsFramework():
    # testdatapath is the location of example files to test with
    testdatapath = './data/tests/'
    # vocabpath is the location of vocabulary files to test with
    vocabpath = './data/vocabularies/'

    # following are files used as input during the tests, don't remove these
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    monthvocabfile = vocabpath + 'month.txt'
    testmonthvocabfile = testdatapath + 'test_month.txt'
    geogvocabfile = vocabpath + 'dwc_geography.txt'
    darwincloudfile = vocabpath + 'darwin_cloud.txt'
    geogcountfileutf8 = testdatapath + "test_geography_count_utf8.csv"
    geogfileutf8 = testdatapath + "test_geography_utf8.csv"

    # following are files output during the tests, remove these in dispose()
    tsvfromcsvfile1 = testdatapath + 'test_tsv_from_csv_1.txt'
    tsvfromcsvfile2 = testdatapath + 'test_tsv_from_csv_2.txt'
    testvocabfile = testdatapath + 'test_vocab_file.csv'
    writevocabheadertestfile = testdatapath + 'test_write_vocabheader.txt'
    recommendedreporttestfile = testdatapath + 'test_term_recommended_report.txt'
    termcountreporttestfile = testdatapath + 'test_term_count_report.txt'
    counttestfile = testdatapath + 'test_three_specimen_records.txt'

    def dispose(self):
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        recommendedreporttestfile = self.recommendedreporttestfile
        termcountreporttestfile = self.termcountreporttestfile
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
        geogcountfileutf8 = self.framework.geogcountfileutf8
        geogfileutf8 = self.framework.geogfileutf8
        dialect = vocab_dialect()
        
        for field in controlledtermlist:
            vocabfile = vocabpath + field + '.txt'
            if not os.path.isfile(vocabfile):
                success = writevocabheader(vocabfile, vocabfieldlist, dialect)
            self.assertTrue(os.path.isfile(vocabfile), vocabfile + ' does not exist')

        self.assertTrue(os.path.isfile(geogvocabfile), geogvocabfile + ' does not exist')

        s = geogcountfileutf8 + ' does not exist'
        self.assertTrue(os.path.isfile(geogcountfileutf8), s)

        s = geogfileutf8 + ' does not exist'
        self.assertTrue(os.path.isfile(geogfileutf8), s)

    def test_vocab_headers_correct(self):
        print 'testing vocab_headers_correct'
        vocabpath = self.framework.vocabpath
        vocabdialect = vocab_dialect()
        vocabencoding = 'utf-8'
        
        for field in controlledtermlist:
            vocabfile = vocabpath + field + '.txt'
            if not os.path.isfile(vocabfile):
                success = writevocabheader(vocabfile, vocabfieldlist, vocabdialect, 
                    vocabencoding)
            header = read_header(vocabfile, vocabdialect, vocabencoding)
            expected = [field.lower()] + vocabfieldlist
            s = 'File: %s\nheader: %s\n' % (vocabfile, header)
            s += 'not as expected: %s' % expected
            self.assertEqual(header, expected, s)

    def test_read_vocab_header(self):
        print 'testing read_vocab_header'
        vocabdialect = vocab_dialect()
        vocabencoding = 'utf-8'
        
        monthvocabfile = self.framework.monthvocabfile
        header = read_header(monthvocabfile, vocabdialect, vocabencoding)
        found = len(header)
        expected = 3
        s = 'Found %s fields in header. Expected %s' % (found, expected)
        self.assertEqual(found, expected, s)

        expected = ['month'] + vocabfieldlist
        s = 'File: %s\nheader: %s\n' % (monthvocabfile, header)
        s += 'not as expected: %s' % expected
        self.assertEqual(header, expected, s)

    def test_read_geog_header(self):
        print 'testing read_geog_header'
        geogvocabfile = self.framework.geogvocabfile
        vocabdialect = vocab_dialect()
        vocabencoding = 'utf-8'

        header = read_header(geogvocabfile, vocabdialect, vocabencoding)
        expected = clean_header(geogvocabheader())

        s = 'File: %s\nheader:\n%s\n' % (geogvocabfile, header)
        s += 'not as expected:\n%s' % expected
        self.assertEqual(header, expected, s)

    def test_vocab_dict_from_file(self):
        print 'testing vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        testmonthvocabfile = self.framework.testmonthvocabfile
        geogcountfileutf8 = self.framework.geogcountfileutf8

        monthdict = vocab_dict_from_file(monthvocabfile, 'month')
        expected = 8

        seek = 'VI'
        s = "%s not found in month dictionary:\n%s" % (seek, monthdict)
        self.assertTrue('VI' in monthdict, s)

        field = 'vetted'
        expected = '1'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'standard'
        expected = '6'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)

        seek = '5'
        s = "%s not found in month dictionary:\n%s" % (seek, monthdict)
        self.assertTrue(seek in monthdict, s)

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

        # Check that the entries in the dictionary are converted using the function
        monthdict = vocab_dict_from_file(testmonthvocabfile, 'month', function=ustripstr)
        # 'vi' is in the vocabfile, upstripstr should convert it to 'VI' in monthdict
        seek = 'VI'

        field = 'vetted'
        expected = '1'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'standard'
        expected = '6'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)

        # 'VII' is in the vocabfile, upstripstr should convert it to 'VII' in monthdict
        seek = 'VII'

        field = 'vetted'
        expected = '1'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)
        field = 'standard'
        expected = '7'
        found = monthdict[seek][field]
        s = "value of %s ('%s') not equal to '%s' " % (field, found, expected)
        s += "for vocab value %s" % seek
        self.assertEqual(found, expected, s)

    def test_missing_vocab_list_from_file(self):
        print 'testing missing_vocab_list_from_file'
        geogcountfileutf8 = self.framework.geogcountfileutf8
        geogfileutf8 = self.framework.geogfileutf8

        v = u'North America|Canada||Alberta|||Brûlé Lake||'
        checklist = [v]
        missinglist = missing_vocab_list_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect())
        s = "missinglist not empty for %s" % v
        self.assertEqual(len(missinglist), 0, s)

        vocabencoding = 'utf-8'
        # Test non-unicode string matching
        v = 'North America|Canada||Alberta|||Brûlé Lake||'
        checklist = [v]
        vocablist = vocab_dict_from_file(geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect(), encoding=vocabencoding)
        missinglist = missing_vocab_list_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect(), encoding=vocabencoding)
        #print 'v: %s' % v
        #print 'checklist: %s' % checklist
        #print 'missinglist: %s' % missinglist
        #print 'vocablist: %s' % vocablist
        s = "missinglist empty for %s" % v
        self.assertEqual(len(missinglist), 1, s)

        # Test unicode string matching
        v = u'North America|Canada||Alberta|||Brûlé Lake||'
        checklist = [v]
        missinglist = missing_vocab_list_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect(), encoding=vocabencoding)
        s = "missinglist not empty for %s" % v
        self.assertEqual(len(missinglist), 0, s)

        v = 'North America|Canada||Alberta|||Brule Lake||'
        checklist = [v]
        missinglist = missing_vocab_list_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect(), encoding=vocabencoding)
        s = "missinglist empty for %s" % v
        self.assertEqual(len(missinglist), 1, s)

    def test_matching_vocab_dict_from_file(self):
        print 'testing matching_vocab_dict_from_file'
        monthvocabfile = self.framework.monthvocabfile
        geogcountfileutf8 = self.framework.geogcountfileutf8

        checklist = ['VI', '5', 'fdsf']
        matchingdict = matching_vocab_dict_from_file(checklist, monthvocabfile, 'month', '|')
        s = 'month vocab at %s does has %s matching items in it instead of 2' % \
            (monthvocabfile, len(matchingdict))
        self.assertEqual(len(matchingdict), 2, s)

        matchingdict = matching_vocab_dict_from_file(checklist, monthvocabfile, 'month')
        s = 'month vocab at %s does has %s matching items in it instead of 2' % \
            (monthvocabfile, len(matchingdict))
        self.assertEqual(len(matchingdict), 2, s)

        self.assertTrue('VI' in matchingdict,"'VI' not found in month dictionary")
        self.assertEqual(matchingdict['VI']['vetted'], '1', 
            "value of 'vetted' not equal to 1 for vocab value 'VI'")
        self.assertEqual(matchingdict['VI']['standard'], '6', 
            "value of 'standard' not equal to '6' for vocab value 'VI'")

        self.assertTrue('5' in matchingdict,"'5' not found in month dictionary")
        self.assertEqual(matchingdict['5']['vetted'], '1', 
            "value of 'vetted' not equal to 1 for vocab value '5'")
        self.assertEqual(matchingdict['5']['standard'], '5', 
            "value of 'standard' not equal to '5' for vocab value '5'")

        v = u'North America|Canada||Alberta|||Brûlé Lake||'
        checklist = [v]
        matchingdict = matching_vocab_dict_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect())
        s = "matchingdict empty for %s" % v
        self.assertEqual(len(matchingdict), 1, s)

        v = 'North America|Canada||Alberta|||Brule Lake||'
        checklist = [v]
        matchingdict = matching_vocab_dict_from_file(checklist, geogcountfileutf8, 
            'continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island',
            dialect=csv_dialect())
        s = "matchingdict empty for %s" % v
        self.assertEqual(len(matchingdict), 0, s)

    def test_terms_not_in_dwc(self):
        print 'testing terms_not_in_dwc'
        checklist = ['eventDate', 'verbatimEventDate', 'year', 'month', 'day', 
        'earliestDateCollected', '', 'latestDateCollected', 'YEAR', 'Year']
        notdwc = terms_not_in_dwc(checklist, casesensitive=True)
        expectedlist = ['YEAR', 'Year', 'earliestDateCollected', 'latestDateCollected']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        checklist = ['eventDate', 'verbatimEventDate', 'year', 'month', 'day', 
        'earliestDateCollected', '', 'latestDateCollected', 'YEAR', 'Year']
        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['EARLIESTDATECOLLECTED', 'LATESTDATECOLLECTED']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        checklist = ['catalogNumber','catalognumber', 'JUNK']
        notdwc = terms_not_in_dwc(checklist, casesensitive=True)
        expectedlist = ['JUNK', 'catalognumber']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        notdwc = terms_not_in_dwc(checklist, casesensitive=False)
        expectedlist = ['JUNK']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        notdwc = terms_not_in_dwc(checklist)
        expectedlist = ['JUNK']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

    def test_terms_not_in_darwin_cloud(self):
        print 'testing terms_not_in_darwin_cloud'
        checklist = ['stuff', 'nonsense', 'Year']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = terms_not_in_darwin_cloud(checklist, darwincloudfile)
        expectedlist = ['NONSENSE', 'STUFF']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        notdwc = terms_not_in_darwin_cloud(checklist, darwincloudfile, vetted=True, 
            casesensitive=True)
        expectedlist = ['Year', 'nonsense', 'stuff']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        notdwc = terms_not_in_darwin_cloud(checklist, darwincloudfile, vetted=True, 
            casesensitive=False)
        expectedlist = ['NONSENSE', 'STUFF']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

    def test_darwinize_list(self):
        print 'testing darwinize_list'
        checklist = ['STUFF', 'Nonsense', 'Year', '  ', 'dwc:day', 'MONTH ', \
            'lifestage', 'Id']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = darwinize_list(checklist, darwincloudfile)
        expectedlist = ['STUFF', 'Nonsense', 'year', 'UNNAMED_COLUMN_1', 'day', 'month', \
            'lifeStage', 'Id']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        checklist = ['InstitutionCode ', 'collectioncode', 'DATASETNAME']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = darwinize_list(checklist, darwincloudfile)
        expectedlist = ['institutionCode', 'collectionCode', 'datasetName']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

        checklist = [u'catalogNumber ', u'InstitutionCode ', u'CollectionCode ', u'Id']
        darwincloudfile = self.framework.darwincloudfile
        notdwc = darwinize_list(checklist, darwincloudfile)
        expectedlist = ['catalogNumber', 'institutionCode', 'collectionCode', 'Id']
        s = 'Found:\n%s\nNot as expected:\n%s' % (notdwc, expectedlist)
        self.assertEqual(notdwc, expectedlist, s)

    def test_not_in_list(self):
        print 'testing not_in_list'
        targetlist = ['b', 'a', 'c']
        checklist = ['c', 'd', 'a', 'e']
        newlist = not_in_list(targetlist, checklist)
        self.assertEqual(newlist, ['d', 'e'],
            'new values de for target list do not meet expectation')
        newlist = not_in_list(None, checklist)
        self.assertEqual(newlist, ['a', 'c', 'd', 'e'],
            'new values acde for targetlist do not meet expectation')

    def test_distinct_vocabs_to_file(self):
        print 'testing distinct_vocabs_to_file'
        testvocabfile = self.framework.testvocabfile
        vocabencoding = 'utf8'

        valuelist = ['b', 'a', 'c']
        writtenlist = distinct_vocabs_to_file(testvocabfile, valuelist, 'verbatim')
        expected = ['a', 'b', 'c']

        # Check that the testvocabfile exists
        s = 'writtenlist: %s not as expected: %s' % (writtenlist, expected)
        self.assertEqual(writtenlist, expected, s)
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for first checklist' % testvocabfile
        self.assertTrue(check, s)

        fulllist = extract_values_from_file(testvocabfile, ['verbatim'], separator=None,
            dialect=None, encoding=vocabencoding)        
        checklist = ['c', 'd', 'a', 'e']
        writtenlist = distinct_vocabs_to_file(testvocabfile, checklist, 'verbatim')
        expected = ['d', 'e']
        s = 'writtenlist: %s not as expected: %s' % (writtenlist, expected)
        self.assertEqual(writtenlist, expected, s)
        check = os.path.isfile(testvocabfile)
        s = 'testvocabfile not written to %s for second checklist' % testvocabfile
        self.assertTrue(check, s)

        fulllist = extract_values_from_file(testvocabfile, ['verbatim'], separator=None,
            dialect=None, encoding=vocabencoding)
        expected = ['a', 'b', 'c', 'd', 'e']
        s = 'Extracted values: %s\n not as expected: %s' % (fulllist, expected)
        self.assertEqual(fulllist, expected, s)

    def test_compose_key_from_list(self):
        print 'testing compose_key_from_list'
        valuelist = ['a', 'b', 'c']
        key = compose_key_from_list(valuelist, '|')
        expected = 'a|b|c'
        self.assertEqual(key, expected, 
            'key value' + key + 'not as expected: ' + expected)

        key = compose_key_from_list(valuelist)
        expected = 'abc'
        self.assertEqual(key, expected, 
            'key value' + key + 'not as expected: ' + expected)

        key = compose_key_from_list(geogkeytermlist, '|')
        expected = 'continent|country|countryCode|stateProvince|county|municipality|waterBody|islandGroup|island'
        self.assertEqual(key, expected, 
            'geog key value:\n' + key + '\nnot as expected:\n' + expected)

        key = compose_key_from_list(geogkeytermlist)
        expected = 'continentcountrycountryCodestateProvincecountymunicipalitywaterBodyislandGroupisland'
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
        header = vocabheader(keyfields, '|')
        expected = [keyfields] + ['country', 'stateprovince', 'county'] + vocabfieldlist
        s = 'header:\n%s\nnot as expected:\n%s' % (header,expected)
        self.assertEqual(header, expected, s)

        header = vocabheader(keyfields)
        expected = [keyfields] + vocabfieldlist
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
        expected = [
            'geogkey', 'continent', 'country', 'countryCode', 'stateProvince', 'county', 
            'municipality', 'waterBody', 'islandGroup', 'island', 'standard', 'vetted', 
            'error', 'misplaced', 'unresolved', 'source', 'comment']
        s = 'geog header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_term_values_recommended(self):
        print 'testing term_values_recommended'
        monthvocabfile = self.framework.monthvocabfile
        monthdict = { 
            'V': {'vetted':'1', 'standard':'5'}, 
            'junk': {'vetted':'0', 'standard':None} 
            }
        recommended = term_values_recommended(monthdict)
        expected = { 'V': {'vetted': '1', 'standard': '5'} }
        s = 'added_values:\n%s\nnot as expected:\n%s' \
            % (recommended, expected)
        self.assertEqual(recommended, expected, s)

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

        d = compose_dict_from_key(key, termlist, '|')
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

        k = compose_key_from_row(row, terms, separator=	'|')
        expected = '|United States|US'
        s = 'key %s not as expected %s' % (k, expected)
        self.assertEqual(k, expected, s)

        k = compose_key_from_row(row, terms)
        expected = ''
        s = 'key %s not as expected %s' % (k, expected)
        self.assertEqual(k, expected, s)

if __name__ == '__main__':
    print '=== dwca_vocab_utils.py ==='
    #setup_actor_logging({'loglevel':'DEBUG'})
    unittest.main()
