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
__version__ = "dwca_vocab_utils.py 2016-02-05T16:54-03:00"

# This file contains common utility functions for dealing with the vocabulary management
# for Darwin Core-related terms
#
# Example:
#
# python dwca_vocab_utils.py

from dwca_terms import vocabfieldlist
from dwca_utils import csv_file_dialect
from dwca_utils import read_header
from dwca_terms import simpledwctermlist
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
    dialect = csv.excel
    dialect.lineterminator='\r'
    dialect.delimiter=','
    dialect.escapechar='/'
    dialect.doublequote=True
    dialect.quotechar='"'
    dialect.quoting=csv.QUOTE_MINIMAL
    dialect.skipinitialspace=True
    dialect.strict=False
    return dialect

def get_standard_value(was, valuedict):
    """Get the standard value of a term from a dictionary.
    parameters:
        was - the value of the term to standardize
        valuedict - the dictionary to lookup the standard value
    returns:
        valuedict[was] - the standard value of the term, if it exists, else None"""
    if was is None:
        return None
    if was in valuedict.keys():
        return valuedict[was]
    return None

def distinct_vocab_list_from_file(vocabfile, dialect=None):
    """Get the list of distinct verbatim values in an existing vocabulary lookup file.
    parameters:
        vocabfile - the full path to the vocabulary lookup file
        dialect - a csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        sorted(list(values)) - a sorted list of distinct verbatim values in the vocabulary
    """
#    print 'vocabfile: %s\nvocabfieldlist:%s' % (vocabfile, vocabfieldlist)
    if os.path.isfile(vocabfile) == False:
        return None
    values = set()
    if dialect is None:
        dialect = vocab_dialect()
    with open(vocabfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        i=0
        for row in dr:
            # Skip the header row.
            if i>0:
                values.add(row['verbatim'])
            i+=1
    return sorted(list(values))

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
    if os.path.isfile(inputfile) == False:
        return None
    values = set()
    if dialect is None:
        dialect = csv_file_dialect(inputfile)
    header = read_header(inputfile, dialect)
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
    """Get the list of distinct values in list that are not in a target list already.
    parameters:
        targetlist - the list to check to see if the value already exists there
        checklist - the list of values to check against the targetlist
    returns:
        sorted(list(values)) - a sorted list of distinct new values not in the target list
    """
    if targetlist is None:
        return sorted(checklist)
    if checklist is None:
        return None
    newlist = []
    for v in checklist:
        if v not in targetlist:
            newlist.append(v)
    if '' in newlist:
        newlist.remove('')
    return sorted(newlist)

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
            writer.writerow({'verbatim':term })
    return newvaluelist

class DWCAUtilsFramework():
    # testdatapath is the location of the files to test with
    testdatapath = '../../data/tests/'

    # following are files used as input during the tests, don't remove these
    csvreadheaderfile = testdatapath + 'test_eight_specimen_records.csv'
    tsvreadheaderfile = testdatapath + 'test_three_specimen_records.txt'
    tsvtest1 = testdatapath + 'test_tsv_1.txt'
    tsvtest2 = testdatapath + 'test_tsv_2.txt'
    csvtest1 = testdatapath + 'test_csv_1.csv'
    csvtest2 = testdatapath + 'test_csv_2.csv'
    csvtotsvfile1 = testdatapath + 'test_csv_1.csv'
    csvtotsvfile2 = testdatapath + 'test_csv_2.csv'
    csvcompositepath = testdatapath + 'test_csv*.csv'
    tsvcompositepath = testdatapath + 'test_tsv*.txt'
    mixedcompositepath = testdatapath + 'test_*_specimen_records.*'
    monthvocabfile = testdatapath + 'test_vocab_month.csv'
    geogvocabfile = testdatapath + 'test_dwcgeography.csv'
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'

    # following are files output during the tests, remove these in dispose()
    csvwriteheaderfile = testdatapath + 'test_write_header_file.csv'
    tsvfromcsvfile1 = testdatapath + 'test_tsv_from_csv_1.txt'
    tsvfromcsvfile2 = testdatapath + 'test_tsv_from_csv_2.txt'
    testvocabfile = testdatapath + 'test_vocab_file.csv'

    def dispose(self):
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        if os.path.isfile(csvwriteheaderfile):
            os.remove(csvwriteheaderfile)
        if os.path.isfile(tsvfromcsvfile1):
            os.remove(tsvfromcsvfile1)
        if os.path.isfile(tsvfromcsvfile2):
            os.remove(tsvfromcsvfile2)
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        return True

class DWCAUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = DWCAUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_get_standard_value(self):
        testdict = { 'm':'male', 'M':'male', 'male':'male', 'f':'female', 'F':'female', 
            'female':'female'}
        self.assertIsNone(get_standard_value('unnoewn', testdict), 
            "lookup 'unnoewn' does not return None")
        self.assertIsNone(get_standard_value(None, testdict), 
            'lookup None does not return None')
        self.assertEqual(get_standard_value('m', testdict), 'male', 
            "lookup 'm' does not return 'male'")
        self.assertEqual(get_standard_value('M', testdict), 'male', 
            "lookup 'M' does not return 'male'")
        self.assertEqual(get_standard_value('male', testdict), 'male', 
            "lookup 'male' does not return 'male'")
        self.assertEqual(get_standard_value('f', testdict), 'female', 
            "lookup 'f' does not return 'female'")
        self.assertEqual(get_standard_value('F', testdict), 'female', 
            "lookup 'F' does not return 'female'")
        self.assertEqual(get_standard_value('female', testdict), 'female', 
            "lookup 'female' does not return 'female'")

    def test_distinct_vocab_list_from_file(self):
        monthvocabfile = self.framework.monthvocabfile
        months = distinct_vocab_list_from_file(monthvocabfile)
#        print 'months: %s' % months
        self.assertEqual(len(months), 6, 
            'the number of distinct verbatim month values does not match expectation')
        self.assertEqual(months, ['5', 'V', 'VI', 'Vi', 'v', 'vi'],
            'verbatim month values do not match expectation')

    def test_distinct_term_values_from_file(self):
        monthvocabfile = self.framework.monthvocabfile
        months = distinct_term_values_from_file(monthvocabfile, 'verbatim')
#        print 'months: %s' % months
        self.assertEqual(len(months), 6, 
            'the number of distinct verbatim month values does not match expectation')
        self.assertEqual(months, ['5', 'V', 'VI', 'Vi', 'v', 'vi'],
            'verbatim month values do not match expectation')

    def test_distinct_composite_term_values_from_file(self):
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
        self.assertEqual(geogs, ['United States||San Bernardino', 'United States||Honolulu', 'United States||', 'United States||Kern', 'United States||Chelan'],
            'composite geogs values do not match expectation')

        geogs = distinct_composite_term_values_from_file(testfile, 
            'country|stateProvince|county', '|')
#        print 'geogs: %s' % geogs
        self.assertEqual(geogs, ['United States|Colorado|', 'United States|California|', 'United States|Washington|Chelan', 'United States|Hawaii|Honolulu', 'United States|California|San Bernardino', 'United States|California|Kern'],
            'composite geogs values do not match expectation')

    def test_terms_not_in_dwc(self):
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
        valuelist = ['a', 'b', 'c']
        key = compose_key_from_list(valuelist)
        expected = 'a|b|c'
        self.assertEqual(key, expected, 
            'key value' + key + 'not as expected: ' + expected)

if __name__ == '__main__':
    unittest.main()
