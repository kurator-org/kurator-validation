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
__version__ = "dwca_utils.py 2016-05-11T22:45-03:00"

# This file contains common utility functions for dealing with the content of CSV and
# TSV data. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python dwca_utils.py

import os.path
import json
import glob
import unittest
import re
try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    # jython pip install unicodecsv for use in workflows
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

tokenreportfieldlist = ['token', 'rowcount', 'totalcount']

def tsv_dialect():
    """Get a dialect object with TSV properties.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with TSV attributes"""
    dialect = csv.excel_tab
    dialect.lineterminator='\r'
    dialect.delimiter='\t'
    dialect.escapechar='/'
    dialect.doublequote=True
    dialect.quotechar='"'
    dialect.quoting=csv.QUOTE_NONE
    dialect.skipinitialspace=True
    dialect.strict=False
    return dialect
    
def csv_file_dialect(fullpath):
    """Detect the dialect of a CSV or TXT data file.
    parameters:
        fullpath - full path to the file to process
    returns:
        dialect - a csv.dialect object with the detected attributes
    """
    # Cannot function without a file
    if fullpath is None or len(fullpath)==0:
        return None

    # Cannot function without an actual file where full path points
    if os.path.isfile(fullpath) == False:
        return None

    # Let's look at up to readto bytes from the file
    readto = 4096
    filesize = os.path.getsize(fullpath)
    if filesize < readto:
        readto = filesize

    with open(fullpath, 'rb') as file:
        # Try to read the specified part of the file
        try:
            buf = file.read(readto)
#            print 'buf:\n%s' % buf
            # Make a determination based on existence of tabs in the buffer, as the
            # Sniffer is not particularly good at detecting TSV file formats. So, if the
            # buffer has a tab in it, let's treat it as a TSV file 
            if buf.find('\t')>0:
                return tsv_dialect()
#            dialect = csv.Sniffer().sniff(file.read(readto))
            # Otherwise let's see what we can find invoking the Sniffer.
            dialect = csv.Sniffer().sniff(buf)
        except csv.Error:
            # Something went wrong, so let's try to read a few lines from the beginning of 
            # the file
            try:
                file.seek(0)
#                print 'Re-sniffing with tab to %s' % (readto)
                sample_text = ''.join(file.readline() for x in xrange(2,4,1))
                dialect = csv.Sniffer().sniff(sample_text)
            # Sorry, couldn't figure it out
            except csv.Error:
#                print 'No dice'
                return None
    
    # Fill in some standard values for the remaining dialect attributes        
    if dialect.escapechar is None:
        dialect.escapechar='/'
    dialect.skipinitialspace=True
    dialect.strict=False
    return dialect

def dialect_attributes(dialect):
    if dialect is None:
        return 'no dialect given'
    s = 'lineterminator: ' 
    if dialect.lineterminator == '\r':
        s+= '{CR}'
    elif dialect.lineterminator == '\n':
        s+= '{NL}'
    elif dialect.lineterminator == '\r\n':
        s+= '{CR}{NL}'
    else: 
        s += dialect.lineterminator

    s += '\ndelimiter: '
    if dialect.delimiter == '\t':
        s+= '{TAB}'
    else:
        s+= dialect.delimiter

    s += '\nescapechar: ' 
    s += dialect.escapechar

    s += '\ndoublequote: '
    if dialect.doublequote == True:
        s += 'True' 
    else:
        s += 'False' 

    s += '\nquotechar: ' 
    s += dialect.quotechar

    s += '\nquoting: ' 
    if dialect.quoting == csv.QUOTE_NONE:
        s += 'csv.QUOTE_NONE'
    elif dialect.quoting == csv.QUOTE_MINIMAL:
        s += 'csv.QUOTE_MINIMAL'
    elif dialect.quoting == csv.QUOTE_NONNUMERIC:
        s += 'csv.QUOTE_NONNUMERIC'
    elif dialect.quoting == csv.QUOTE_ALL:
        s += 'csv.QUOTE_ALL'

    s += '\nskipinitialspace: ' 
    if dialect.skipinitialspace == True:
        s += 'True'
    else:
        s += 'False'

    s += '\nstrict: ' 
    if dialect.strict == True:
        s += 'True'
    else:
        s += 'False'
    return s

def read_header(fullpath, dialect = None):
    """Get the header line of a CSV or TXT data file.
    parameters:
        fullpath - the full path to the file to process
        dialect - a csv.dialect object with the attributes of the input file
    returns:
        header - a list containing the fields in the original header
    """
    # Cannot function without a file
    if fullpath is None or len(fullpath)==0:
        return None

    # Cannot function without an actual file where full path points
    if os.path.isfile(fullpath) == False:
        return None

    header = None

    # If no explicit dialect for the file is given, figure it out from the file
    if dialect is None:
        dialect = csv_file_dialect(fullpath)

    # Open up the file for processing
    with open(fullpath, 'rU') as csvfile:
        reader = csv.DictReader(csvfile, dialect=dialect)
        # header is the list as returned by the reader
        header=reader.fieldnames

    # Return the header from the file
    return header

def composite_header(fullpath, dialect = None):
    """Get a header that includes all of the fields in headers of a set of files in the 
       given path.
    parameters:
        fullpath - the full path to the files to process. (e.g., './*.txt')
        dialect - a csv.dialect object with the attributes of the input files, which must
           all have the same dialect if dialect is given, otherwise it will be detected.
    returns:
        compositeheader - a list containing the fields in the header
    """
    if fullpath is None:
          return None
    compositeheader = None
    usedialect = dialect
    files = glob.glob(fullpath)
    if files is None:
        return None
    for file in files:
        if dialect is None:
            usedialect = csv_file_dialect(file)
        header = read_header(file, usedialect)
        compositeheader = merge_headers(compositeheader, header)
    return compositeheader

def write_header(fullpath, fieldnames, dialect):
    """Write the header line of a CSV or TXT data file.
    parameters:
        fullpath - the full path to the file to process.
        fieldnames -  a list containing the fields in the header
        dialect - a csv.dialect object with the attributes of the input file
    returns:
        success - True is the header was written to file"""
    success = True
    with open(fullpath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        try:
            writer.writeheader()
        except:
            success = False
    return success

def header_map(header):
    """Construct a map between a header and a cleaned version of the header.
    parameters:
        header - the header to clean
    returns:
        headermap - a map of the keys in the cleaned header to the original field names
    """
    headermap = {}
    for field in header:
        cleanfield = slugify(field)
        headermap[cleanfield]=field
    return headermap

def clean_header(header):
    """Construct a header from the cleaned field names in a header.
    parameters:
        header - the header to clean
    returns:
        cleanheader - the header after cleaning
    """
    # Cannot function without a header
    if header is None or len(header)==0:
        return None

    cleanheader = []
    i=1

    # Clean every field in the header and append it to the cleanheader
    for field in header:
        cleanfield = slugify(field)
        if len(cleanfield)==0:
            cleanfield = 'field%s' % i
        cleanheader.append(cleanfield)
        i+=1

    # Return a version of the header that has been cleaned
    return cleanheader

def slugify(s, length=None, separator="-"):
    """Construct a slugged version of supplied string.
    parameters:
        s - the target string
        length - the maximum length token from s to keep
        separator - the character to put in the place of whitespace
    returns:
        ret.strip() - lower case, accent-removed, stripped version of input string
    """
    s = re.sub('[^a-zA-Z\d\s:]', ' ', s)
    if length:
        words = s.split()[:length]
    else:
        words = s.split()
    s = ' '.join(words)
    ret = ''
    for c in s.lower():
        try:
            ret += htmlentitydefs.codepoint2name[ord(c)]
        except:
            ret += c
    ret = re.sub('([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)', r'\1', ret)
    ret = ret.strip()
    ret = re.sub(' ', '_', ret)
    ret = re.sub('\W', '', ret)
    ret = re.sub('[ _]+/', separator, ret)
    return ret.strip()

def merge_headers(headersofar, headertoadd = None):
    """Construct a header from the distinct white-space-stripped fields in two headers.
    parameters:
        headersofar - the first header from which to build the composite
        headertoadd -  a header to merge with the first header
    returns:
        sorted(list(composedheader)) - a sorted list of the combined header
    """
    composedheader = set()
    if headersofar is None and headertoadd is None:
        return None
    if headersofar is not None:
        for field in headersofar:
            addme = field.strip()
            if len(addme) > 0:
                composedheader.add(addme)
    if headertoadd is not None:
        for field in headertoadd:
            addme = field.strip()
            if len(addme) > 0:
                composedheader.add(addme)
    if len(composedheader) == 0:
        return None
    return sorted(list(composedheader))

def csv_to_tsv(inputfile, outputfile):
    """Convert an arbitrary csv file into a standardized tsv file.
    parameters:
        inputfile - the full path to the file to convert. (e.g., './infile.txt')
        outputfile - the full path to the converted file. (e.g., './outfile.txt')
    returns:
        True if finished successfully
    """
    if inputfile is None or len(inputfile) == 0:
        return None
    if outputfile is None or len(outputfile) == 0:
        return None
    if os.path.isfile(inputfile) == False:
        return None
    # discern the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputheader = read_header(inputfile,inputdialect)
    with open(outputfile, 'a') as tsvfile:
        writer = csv.DictWriter(tsvfile, dialect=tsv_dialect(), fieldnames=inputheader)
        writer.writeheader()
#        for row in read_csv_row_tuple(inputfile, inputdialect):
        for row in read_csv_row(inputfile, inputdialect):
            writer.writerow(row)
    return True

def term_rowcount_from_file(inputfile, termname):
    """Count of the rows that are populated for a given term
    parameters:
        inputfile - the full path to the file to assess
        termname - the term for which to count rows
    returns:
        rowcount - the number of rows with the term populated
    """
    if inputfile is None or len(inputfile) == 0:
        return 0
    if termname is None or len(termname) == 0:
        return 0
    if os.path.isfile(inputfile) == False:
        return 0
    # discern the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputheader = read_header(inputfile,inputdialect)
    if termname not in inputheader:
        return 0
    rowcount = 0
    for row in read_csv_row(inputfile, inputdialect):
        try:
            value = row[termname]
            if value is not None and len(value.strip()) > 0:
                rowcount += 1
        except:
            pass
    return rowcount

def term_token_count_from_file(inputfile, termname):
    """Make a dictionary of the tokens and their number of occurrences for a given term
    parameters:
        inputfile - the full path to the file to assess
        termname - the term for which to count rows
    returns:
        tokens - a dictionary containing the tokens and their statistics
    """
    if inputfile is None or len(inputfile) == 0:
        return 0
    if termname is None or len(termname) == 0:
        return 0
    if os.path.isfile(inputfile) == False:
        return 0
    # discern the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputheader = read_header(inputfile,inputdialect)
    if termname not in inputheader:
        return None
    rowcount = 0
    tokencount = 0
    populatedrowcount = 0
    tokens = { 'tokenlist':{} }
    for row in read_csv_row(inputfile, inputdialect):
        try:
            value = row[termname]
        except:
            pass
#        print '%s: %s' % (termname, value)
        if value is not None and len(value.strip()) > 0:
            rowdict = {}
            wordlist = re.sub("[^\w]", " ",  value).split()
#                print '%s: %s' % (termname, wordlist)
            for token in wordlist:
#                    print 'token: %s' % token
                if token in rowdict:
                    rowdict[token]['totalcount']=rowdict[token]['totalcount']+1
                else:
                    rowdict[token]={}
                    rowdict[token]['rowcount']=1
                    rowdict[token]['totalcount']=1
#                    print 'rowdict: %s' % rowdict
            populatedrowcount += 1
            for key, value in rowdict.iteritems():
                tokenlist = tokens['tokenlist']
                if key in tokenlist:
                    tokenlist[key]['rowcount'] = \
                        tokenlist[key]['rowcount'] + value['rowcount']
                    tokenlist[key]['totalcount'] = \
                        tokenlist[key]['totalcount'] + value['totalcount']
                else:
                    tokenlist[key] = {}
                    tokenlist[key]['rowcount'] = value['rowcount']
                    tokenlist[key]['totalcount'] = value['totalcount']
#                print 'token: %s\nwordlist: %s\ntokens: %s' % (token, wordlist, tokens)
        rowcount += 1
        tokencount += len(wordlist)
    tokens['rowcount']=rowcount
    tokens['tokencount']=tokencount
    tokens['input']=inputfile
    tokens['term']=termname
    return tokens

def token_report(reportfile, tokens, dialect=None):
    """Write a term token report to a file.
    parameters:
        reportfile - the full path to the report file
        tokens - a dictionary of token occurrences (see output from 
            term_token_count_from_file()
        dialect - a csv.dialect object with the attributes of the report file
    returns:
        success - True if the report was written, else False
    """
    if tokens is None or len(tokens)==0:
        return False

    if dialect is None:
        dialect = tsv_dialect()
    
    if reportfile is not None:
        with open(reportfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=tokenreportfieldlist)
            writer.writeheader()

        if os.path.isfile(reportfile) == False:
            return False

#        print 'tokens: %s' % (tokens)
        with open(reportfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=tokenreportfieldlist)
            for key, value in tokens['tokenlist'].iteritems():
#                print ' key: %s value: %s' % (key, value)
                writer.writerow({'token':key, 'rowcount':value['rowcount'], \
                    'totalcount':value['totalcount'] })
    else:
        # print the report
        for key, value in tokens['tokenlist'].iteritems():
            print 'token: %s rowcount: %s totalcount: %s' % (key, value['rowcount'], \
                value['totalcount'])
    return True

def csv_field_checker(inputfile):
    """Determine if any row in a csv file has fewer fields than the header.
    parameters:
        inputfile - the full path to the file to convert. (e.g., './infile.txt')
    returns:
        index, row - a tuple composed of the index of the first row that has a different 
            number of fields (1 is the first row after the header) and the row string
    """
    if inputfile is None or len(inputfile) == 0:
        return None
    if os.path.isfile(inputfile) == False:
        return None
    # discern the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    delimiter = inputdialect.delimiter
    header = read_header(inputfile,inputdialect)
    if header is None:
        return None
    fieldcount = len(header)
#    print 'header: %s fields\n%s' % (fieldcount, header)
    with open(inputfile, 'rU') as f:
        i=0
        for line in f:
            delimitercount = line.count(delimiter)
            if delimitercount < fieldcount-1:
#                print 'row: %s fields\n%s' % (delimitercount, line)
                return i, line
            i+=1
    return None

# def header_as_tuple(header):
#     header_tuple = ()
#     for field in header:
#         field_as_tuple = (field,)
#         header_tuple = header_tuple + field_as_tuple
#     return header_tuple

# def read_csv_row_tuple(path, dialect):
#     header = read_header(path, dialect)
#     fields = header_as_tuple(header)
#     Record = namedtuple('Record', fields)
#     with open(path, 'rU') as data:
#         data.readline()            # Skip the header
#         reader = csv.reader(data, dialect)  # Create a regular tuple reader
#         for row in map(Record._make, reader):
#             yield row

def read_csv_row(path, dialect):
    with open(path, 'rU') as data:
        reader = csv.DictReader(data, dialect=dialect)
        for row in reader:
            yield row

def split_path(fullpath):
    """Parse out the path to, the name of, and the extension for a given file.
    parameters:
        fullpath - the full path to the file to process. (e.g., './thefile.txt')
    returns:
        path - the path to the file (e.g., './')
        filext - the extension for the file name (e.g., 'thefile')
        filepattern - the file name without the path and extension (e.g., 'txt')"""
    if fullpath is None or len(fullpath)==0:
        return None, None, None
    path = fullpath[:fullpath.rfind('/')]
    fileext = fullpath[fullpath.rfind('.')+1:]
    filepattern = fullpath[fullpath.rfind('/')+1:fullpath.rfind('.')]
    return path, fileext, filepattern

def response(returnvars, returnvals):
    response = {}
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return response
    
class DWCAUtilsFramework():
    # testdatapath is the location of the files to test with
    testdatapath = './data/tests/'

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
    monthvocabfile = testdatapath + 'test_vocab_month.txt'
    geogvocabfile = testdatapath + 'test_dwcgeography.txt'
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile1 = testdatapath + 'test_fieldcount.csv'
    fieldcountestfile2 = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile3 = testdatapath + 'test_bad_fieldcount1.txt'
    termrowcountfile1 = testdatapath + 'test_eight_specimen_records.csv'
    termrowcountfile2 = testdatapath + 'test_three_specimen_records.txt'
    termtokenfile = testdatapath + 'test_eight_specimen_records.csv'

    # following are files output during the tests, remove these in dispose()
    csvwriteheaderfile = testdatapath + 'test_write_header_file.csv'
    tsvfromcsvfile1 = testdatapath + 'test_tsv_from_csv_1.txt'
    tsvfromcsvfile2 = testdatapath + 'test_tsv_from_csv_2.txt'
    testvocabfile = testdatapath + 'test_vocab_file.csv'
    testtokenreportfile = testdatapath + 'test_token_report_file.txt'

    def dispose(self):
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        testtokenreportfile = self.testtokenreportfile
        if os.path.isfile(csvwriteheaderfile):
            os.remove(csvwriteheaderfile)
        if os.path.isfile(tsvfromcsvfile1):
            os.remove(tsvfromcsvfile1)
        if os.path.isfile(tsvfromcsvfile2):
            os.remove(tsvfromcsvfile2)
        if os.path.isfile(testvocabfile):
            os.remove(testvocabfile)
        if os.path.isfile(testtokenreportfile):
            os.remove(testtokenreportfile)
        return True

class DWCAUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = DWCAUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        csvreadheaderfile = self.framework.csvreadheaderfile
        tsvreadheaderfile = self.framework.tsvreadheaderfile
        tsvtest1 = self.framework.tsvtest1
        tsvtest2 = self.framework.tsvtest2
        csvtest1 = self.framework.csvtest1
        csvtest2 = self.framework.csvtest2
        csvtotsvfile1 = self.framework.csvtotsvfile1
        csvtotsvfile2 = self.framework.csvtotsvfile2
        geogvocabfile = self.framework.geogvocabfile
        compositetestfile = self.framework.compositetestfile
        fieldcountestfile1 = self.framework.fieldcountestfile1
        fieldcountestfile2 = self.framework.fieldcountestfile2
        fieldcountestfile3 = self.framework.fieldcountestfile3
        monthvocabfile = self.framework.monthvocabfile

        self.assertTrue(os.path.isfile(csvreadheaderfile), csvreadheaderfile + ' does not exist')
        self.assertTrue(os.path.isfile(tsvreadheaderfile), tsvreadheaderfile + ' does not exist')
        self.assertTrue(os.path.isfile(tsvtest1), tsvtest1 + ' does not exist')
        self.assertTrue(os.path.isfile(tsvtest2), tsvtest2 + ' does not exist')
        self.assertTrue(os.path.isfile(csvtest1), csvtest1 + ' does not exist')
        self.assertTrue(os.path.isfile(csvtest2), csvtest2 + ' does not exist')
        self.assertTrue(os.path.isfile(csvtotsvfile1), csvtotsvfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(csvtotsvfile2), csvtotsvfile2 + ' does not exist')
        self.assertTrue(os.path.isfile(monthvocabfile), monthvocabfile + ' does not exist')
        self.assertTrue(os.path.isfile(geogvocabfile), geogvocabfile + ' does not exist')
        self.assertTrue(os.path.isfile(compositetestfile), compositetestfile + ' does not exist')
        self.assertTrue(os.path.isfile(fieldcountestfile1), fieldcountestfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(fieldcountestfile2), fieldcountestfile2 + ' does not exist')
        self.assertTrue(os.path.isfile(fieldcountestfile3), fieldcountestfile3 + ' does not exist')

    def test_tsv_dialect(self):
        print 'testing tsv_dialect'
        dialect = tsv_dialect()
        self.assertEqual(dialect.delimiter, '\t',
            'incorrect delimiter for tsv')
        self.assertEqual(dialect.lineterminator, '\r',
            'incorrect lineterminator for tsv')
        self.assertEqual(dialect.escapechar, '/',
            'incorrect escapechar for tsv')
        self.assertEqual(dialect.quotechar, '"',
            'incorrect quotechar for tsv')
        self.assertTrue(dialect.doublequote,
            'doublequote not set to True for tsv')
        self.assertEqual(dialect.quoting, 3,
            'quoting not set to csv.QUOTE_NONE for tsv')
        self.assertTrue(dialect.skipinitialspace,
            'skipinitialspace not set to True for tsv')
        self.assertFalse(dialect.strict,
            'strict not set to False for tsv')

    def test_csv_file_dialect(self):
        print 'testing csv_file_dialect'
        csvreadheaderfile = self.framework.csvreadheaderfile
        dialect = csv_file_dialect(csvreadheaderfile)
#        print 'dialect:\n%s' % dialect_attributes(dialect)
        self.assertIsNotNone(dialect, 'unable to detect csv file dialect')
        self.assertEqual(dialect.delimiter, ',',
            'incorrect delimiter detected for csv file')
        self.assertEqual(dialect.lineterminator, '\r\n',
            'incorrect lineterminator for csv file')
        self.assertEqual(dialect.escapechar, '/',
            'incorrect escapechar for csv file')
        self.assertEqual(dialect.quotechar, '"',
            'incorrect quotechar for csv file')
        self.assertFalse(dialect.doublequote,
            'doublequote not set to False for csv file')
        self.assertEqual(dialect.quoting, csv.QUOTE_MINIMAL,
            'quoting not set to csv.QUOTE_MINIMAL for csv file')
        self.assertTrue(dialect.skipinitialspace,
            'skipinitialspace not set to True for csv file')
        self.assertFalse(dialect.strict,
            'strict not set to False for csv file')

    def test_tsv_file_dialect(self):
        print 'testing tsv_file_dialect'
        tsvreadheaderfile = self.framework.tsvreadheaderfile
        dialect = csv_file_dialect(tsvreadheaderfile)
#        print 'dialect:\n%s' % dialect_attributes(dialect)
        self.assertIsNotNone(dialect, 'unable to detect tsv file dialect')
        self.assertEqual(dialect.delimiter, '\t',
            'incorrect delimiter detected for csv file')
        self.assertEqual(dialect.lineterminator, '\r',
            'incorrect lineterminator for csv file')
        self.assertEqual(dialect.escapechar, '/',
            'incorrect escapechar for csv file')
        self.assertEqual(dialect.quotechar, '"',
            'incorrect quotechar for csv file')
        self.assertTrue(dialect.doublequote,
            'doublequote not set to False for csv file')
        self.assertEqual(dialect.quoting, csv.QUOTE_NONE,
            'quoting not set to csv.QUOTE_NONE for csv file')
        self.assertTrue(dialect.skipinitialspace,
            'skipinitialspace not set to True for csv file')
        self.assertFalse(dialect.strict,
            'strict not set to False for csv file')

    def test_read_header1(self):
        print 'testing read_header1'
        csvreadheaderfile = self.framework.csvreadheaderfile
        header = read_header(csvreadheaderfile)
        modelheader = []
        modelheader.append('catalogNumber ')
        modelheader.append('recordedBy')
        modelheader.append('fieldNumber ')
        modelheader.append('year')
        modelheader.append('month')
        modelheader.append('day')
        modelheader.append('decimalLatitude ')
        modelheader.append('decimalLongitude ')
        modelheader.append('geodeticDatum ')
        modelheader.append('country')
        modelheader.append('stateProvince')
        modelheader.append('county')
        modelheader.append('locality')
        modelheader.append('family ')
        modelheader.append('scientificName ')
        modelheader.append('scientificNameAuthorship ')
        modelheader.append('reproductiveCondition ')
        modelheader.append('InstitutionCode ')
        modelheader.append('CollectionCode ')
        modelheader.append('DatasetName ')
        modelheader.append('Id')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 21, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_read_header2(self):
        print 'testing read_header2'
        tsvheaderfile = self.framework.tsvtest1
        header = read_header(tsvheaderfile)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_read_header3(self):
        print 'testing read_header3'
        csvheaderfile = self.framework.csvtest1
        header = read_header(csvheaderfile)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_read_header4(self):
        print 'testing read_header4'
        tsvheaderfile = self.framework.tsvtest2
        header = read_header(tsvheaderfile)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_read_header5(self):
        print 'testing read_header5'
        csvheaderfile = self.framework.csvtest2
        header = read_header(csvheaderfile)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_composite_header(self):
        print 'testing composite_header'
        csvcompositepath = self.framework.csvcompositepath
        tsvcompositepath = self.framework.tsvcompositepath
        mixedcompositepath = self.framework.mixedcompositepath
        header = composite_header(csvcompositepath)
        modelheader = []
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('locality')
        modelheader.append('materialSampleID')
        modelheader.append('phylum')
        modelheader.append('principalInvestigator')
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

        header = composite_header(tsvcompositepath)
        s =  'len(header)=%s' % len(header)
        s += ' len(model)=%s' % len(modelheader)
        s += '\nheader:\n%s' % header
        s += '\nmodel:\n%s' % modelheader
        s += '\ntsvcompositepath: %s' % tsvcompositepath
#        print '%s' % s
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

        header = composite_header(mixedcompositepath)
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
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header),77, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_write_header(self):
        print 'testing write_header'
        csvreadheaderfile = self.framework.csvreadheaderfile
        csvwriteheaderfile = self.framework.csvwriteheaderfile
        header = read_header(csvreadheaderfile)
        dialect = tsv_dialect()
        self.assertIsNotNone(header, 'model header not found')

        written = write_header(csvwriteheaderfile, header, dialect)
        self.assertTrue(written, 'header not written to csvwriteheaderfile')

        writtenheader = read_header(csvwriteheaderfile)

        self.assertEqual(len(header), len(writtenheader),
            'incorrect number of fields in writtenheader')

        self.assertEqual(header, writtenheader,
            'writtenheader not the same as model header')

    def test_csv_to_tsv1(self):
        print 'testing csv_to_tsv1'
        csvfile = self.framework.csvtotsvfile1
        tsvfile = self.framework.tsvfromcsvfile1

        csv_to_tsv(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv not written')

        header = read_header(tsvfile)
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_csv_to_tsv2(self):
        print 'testing csv_to_tsv2'
        csvfile = self.framework.csvtotsvfile2
        tsvfile = self.framework.tsvfromcsvfile2

        csv_to_tsv(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv not written')

        header = read_header(tsvfile, tsv_dialect())
        modelheader = []
        modelheader.append('materialSampleID')
        modelheader.append('principalInvestigator')
        modelheader.append('locality')
        modelheader.append('phylum')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_split_path(self):
        print 'testing split_path'
        path, fileext, filepattern = \
            split_path('../../data/tests/test_eight_specimen_records.csv')
        self.assertEqual(path, '../../data/tests', 'incorrect path')
        self.assertEqual(fileext, 'csv', 'incorrect file extension')
        self.assertEqual(filepattern, 'test_eight_specimen_records', 
            'incorrect file pattern')

    def test_header_map(self):
        print 'testing header_map'
        header = ['b ', ' a', 'c	']
        result = header_map(header)
        self.assertEqual(result, {'b':'b ', 'a':' a', 'c':'c	'}, \
            'header failed to be cleaned properly')

    def test_clean_header(self):
        print 'testing clean_header'
        header = ['b ', ' a', 'c	']
        result = clean_header(header)
        self.assertEqual(result, ['b', 'a', 'c'], 'header failed to be cleaned properly')

    def test_merge_headers(self):
        print 'testing merge_headers'
        header1 = ['b', 'a', 'c']
        header2 = ['b', 'c ', 'd']
        header3 = ['e', 'd	', 'a']
        header4 = []
        header5 = ['']
        header6 = [' ']
        header7 = ['	']
        header8 = ['b', 'a', 'c', '  ']

        result = merge_headers(None)
        s = 'merging without header makes a header when it should not'
        self.assertIsNone(result, )

        result = merge_headers(header4)
        s = 'merging an empty header makes a header when it should not'
        self.assertIsNone(result, s)

        result = merge_headers(header5)
        s = 'merging a header with only a blank field makes a header when it should not'
        self.assertIsNone(result, s)

        result = merge_headers(header6)
        s = 'merging header with only one field composed of a space character makes a '
        s += 'header when it should not'
        self.assertIsNone(result, s)

        result = merge_headers(header7)
        s = 'merging header with only one field composed of a tab character makes a '
        s += 'header when it should not'
        self.assertIsNone(result, s)

        result = merge_headers(None, header1)
        self.assertEqual(result, ['a', 'b', 'c'], 'merged new header did not sort')

        result = merge_headers(header1)
        self.assertEqual(result, ['a', 'b', 'c'], 'merged existing header did not sort')

        result = merge_headers(header1, header1)
        self.assertEqual(result, ['a', 'b', 'c'], 'redundant header merge failed')

        result = merge_headers(header1, header2)
        self.assertEqual(result, ['a', 'b', 'c', 'd'], 'bac-bcd header merge failed')

        result = merge_headers(header1, header2)
        result = merge_headers(result, header3)
        self.assertEqual(result, ['a', 'b', 'c', 'd', 'e'],
            'bac-bcd-eda header merge failed')

        result = merge_headers(header7, header8)
        self.assertEqual(result, ['a', 'b', 'c'],
            'headers with whitespace merge failed')

    def test_csv_field_checker(self):
        print 'testing csv_field_checker'
        csvfile = self.framework.fieldcountestfile2
        result = csv_field_checker(csvfile)
        s = 'field checker found mismatched fields in %s when it should not' % csvfile
        self.assertIsNone(result,s)
        
        csvfile = self.framework.fieldcountestfile1
        result = csv_field_checker(csvfile)
        firstbadrow = result[0]
        s = 'field checker found first mismatched field in %s at row index %s'  \
            % (csvfile, firstbadrow)
        self.assertEqual(firstbadrow,3,s)

        csvfile = self.framework.fieldcountestfile3
        result = csv_field_checker(csvfile)
        firstbadrow = result[0]
        s = 'field checker found first mismatched field in %s at row index %s'  \
            % (csvfile, firstbadrow)
        self.assertEqual(firstbadrow,3,s)

    def test_term_rowcount_from_file(self):
        print 'testing term_rowcount_from_file'
        termrowcountfile = self.framework.termrowcountfile1
        rowcount = term_rowcount_from_file(termrowcountfile,'country')
        expected = 8
        s = 'rowcount (%s) for country does not match expectation (%s)'  \
            % (rowcount, expected)
        self.assertEqual(rowcount,expected,s)

        termrowcountfile = self.framework.termrowcountfile2
        term = 'country'
        expected = 3
        rowcount = term_rowcount_from_file(termrowcountfile,term)
        s = 'rowcount (%s) for %s does not match expectation (%s) in %s'  \
            % (rowcount, term, expected, termrowcountfile)
        self.assertEqual(rowcount,expected,s)

        term = 'island'
        expected = 1
        rowcount = term_rowcount_from_file(termrowcountfile,term)
        s = 'rowcount (%s) for %s does not match expectation (%s) in %s'  \
            % (rowcount, term, expected, termrowcountfile)
        self.assertEqual(rowcount,expected,s)

    def test_term_token_count_from_file(self):
        print 'testing term_token_count_from_file'
        termtokenfile = self.framework.termtokenfile
        termname = 'locality'
        tokens = term_token_count_from_file(termtokenfile, termname)
#        print 'tokens:\n%s' % tokens
        rowcount = 8
        tokencount = 42
        s = 'rowcount found (%s) not as expected (%s)' % (tokens['rowcount'], rowcount)
        self.assertEqual(tokens['rowcount'],rowcount,s)
        s = 'tokencount found (%s) not as expected (%s)' % (tokens['tokencount'], tokencount)
        self.assertEqual(tokens['tokencount'],tokencount,s)
        distincttokencount = 38
        s = 'disincttokencount found (%s) not as expected (%s)' % \
            (len(tokens['tokenlist']), distincttokencount)
        self.assertEqual(len(tokens['tokenlist']),distincttokencount,s)

        value = 'of'
        totalcount = 3
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

        value = 'National'
        totalcount = 2
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

        value = 'Ridge'
        totalcount = 1
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens['tokenlist'][value]['totalcount'], value, totalcount)
        self.assertEqual(tokens['tokenlist'][value]['totalcount'],totalcount,s)

#         termname = 'reproductiveCondition '
#         tokens = term_token_count_from_file(termtokenfile, termname)
#         print 'tokens:\n%s' % tokens

    def test_token_report(self):
        print 'testing token_report'
        termtokenfile = self.framework.termtokenfile
        reportfile = self.framework.testtokenreportfile
        termname = 'locality'
        tokens = term_token_count_from_file(termtokenfile, termname)
        success = token_report(reportfile, tokens)
        self.assertTrue(success,'token report not written to file')

#        print 'tokens from file:\n%s' % tokens

        dialect = tsv_dialect()
        tokens = {}
        with open(reportfile, 'rU') as csvfile:
            dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=tokenreportfieldlist)
            i = 0
            for row in dr:
                if i==0:
                    i = 1
                else:
                    token = row['token']
                    rowcount = row['rowcount']
                    totalcount = row['totalcount']
                    tokens[token] = { 'rowcount':rowcount, 'totalcount':totalcount }
        
#        print 'tokens from report:\n%s' % tokens

        tokencount = 38
        s = 'tokencount (%s) not as expected (%s)' % (len(tokens), tokencount)
        self.assertEqual(len(tokens),tokencount,s)

        value = 'of'
        rowcount = '3'
        totalcount = '3'
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['totalcount'], value, totalcount)
        self.assertEqual(tokens[value]['totalcount'],totalcount,s)
        s = 'rowcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['rowcount'], value, rowcount)
        self.assertEqual(tokens[value]['rowcount'],rowcount,s)

        value = 'National'
        rowcount = '2'
        totalcount = '2'
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['totalcount'], value, totalcount)
        self.assertEqual(tokens[value]['totalcount'],totalcount,s)
        s = 'rowcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['rowcount'], value, rowcount)
        self.assertEqual(tokens[value]['rowcount'],rowcount,s)
 
        value = 'Ridge'
        rowcount = '1'
        totalcount = '1'
        s = 'totalcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['totalcount'], value, totalcount)
        self.assertEqual(tokens[value]['totalcount'],totalcount,s)
        s = 'rowcount (%s) for value "%s" not as expected (%s)' % \
            (tokens[value]['rowcount'], value, rowcount)
        self.assertEqual(tokens[value]['rowcount'],rowcount,s)

if __name__ == '__main__':
    print '=== dwca_utils.py ==='
    unittest.main()
