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
__version__ = "dwca_utils.py 2016-02-10T15:24-03:00"

# This file contains common utility functions for dealing with the content of CSV and
# TSV data. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python dwca_utils.py

#from collections import namedtuple
#from dwca_terms import vocabfieldlist
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
        fullpath - the full path to the file to process.
    returns:
        dialect - a csv.dialect object with the detected attributes"""
    if os.path.isfile(fullpath) == False:
        return None

    readto = 4096
    filesize = os.path.getsize(fullpath)
    if filesize < readto:
        readto = filesize
    with open(fullpath, 'rb') as file:
        try:
#            print 'Sniffing %s to %s' % (fullpath, readto)
            dialect = csv.Sniffer().sniff(file.read(readto))
        except csv.Error:
            try:
                file.seek(0)
#                print 'Re-sniffing with tab to %s' % (readto)
                sample_text = ''.join(file.readline() for x in xrange(2,4,1))
                dialect = csv.Sniffer().sniff(sample_text)
            except csv.Error:
#                print 'No dice'
                return None
        
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
        s+= '\r'
    elif dialect.lineterminator == '\n':
        s+= '\n'
    elif dialect.lineterminator == '\r\n':
        s+= '\r\n'
    else: 
        s += dialect.lineterminator

    s += '\ndelimiter: '
    if dialect.delimiter == '\t':
        s+= '\t'
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
        fullpath - the full path to the file to process.
        dialect - a csv.dialect object with the attributes of the input file
    returns:
        header - a list containing the fields in the original header
    """
    if os.path.isfile(fullpath) == False:
        return None
    header = None
    if dialect is None:
        dialect = csv_file_dialect(fullpath)
    with open(fullpath, 'rU') as csvfile:
        reader = csv.DictReader(csvfile, dialect=dialect)
        # header is the list as returned by the reader
        header=reader.fieldnames
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
    success = False
    with open(fullpath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        writer.writeheader()
        success = True
    return success

def clean_header(header):
    """Construct a header from the white-space-stripped field names in a header.
    parameters:
        header - the header to clean
    returns:
        merge_headers(header) - a sorted list of the header after white space has been
            stripped from field names
    """
    return merge_headers(header)
    
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
#    monthvocabfile = testdatapath + 'test_vocab_month.csv'
    monthvocabfile = testdatapath + 'test_vocab_month.txt'
    geogvocabfile = testdatapath + 'test_dwcgeography.csv'
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile1 = testdatapath + 'test_fieldcount.csv'
    fieldcountestfile2 = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile3 = testdatapath + 'test_bad_fieldcount1.txt'

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

    def test_tsv_dialect(self):
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

#     def test_header_as_tuple(self):
#         header=['a', 'b', 'c']
#         ht = header_as_tuple(header)
#         self.assertEqual(ht[0], 'a', 'tuple construction from header list failed')
#         self.assertEqual(ht[1], 'b', 'tuple construction from header list failed')
#         self.assertEqual(ht[2], 'c', 'tuple construction from header list failed')

    def test_csv_file_dialect(self):
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
        self.assertEqual(dialect.quoting, 0,
            'quoting not set to csv.QUOTE_MINIMAL for csv file')
        self.assertTrue(dialect.skipinitialspace,
            'skipinitialspace not set to True for csv file')
        self.assertFalse(dialect.strict,
            'strict not set to False for csv file')

    def test_tsv_file_dialect(self):
        tsvreadheaderfile = self.framework.tsvreadheaderfile
        dialect = csv_file_dialect(tsvreadheaderfile)
#        print 'dialect:\n%s' % dialect_attributes(dialect)
        self.assertIsNotNone(dialect, 'unable to detect tsv file dialect')
        self.assertEqual(dialect.delimiter, '\t',
            'incorrect delimiter detected for csv file')
        self.assertEqual(dialect.lineterminator, '\r\n',
            'incorrect lineterminator for csv file')
        self.assertEqual(dialect.escapechar, '/',
            'incorrect escapechar for csv file')
        self.assertEqual(dialect.quotechar, '"',
            'incorrect quotechar for csv file')
        self.assertFalse(dialect.doublequote,
            'doublequote not set to False for csv file')
        self.assertEqual(dialect.quoting, 0,
            'quoting not set to csv.QUOTE_MINIMAL for csv file')
        self.assertTrue(dialect.skipinitialspace,
            'skipinitialspace not set to True for csv file')
        self.assertFalse(dialect.strict,
            'strict not set to False for csv file')

    def test_read_header1(self):
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

    def test_composite_header1(self):
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
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
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
        path, fileext, filepattern = \
            split_path('../../data/tests/test_eight_specimen_records.csv')
        self.assertEqual(path, '../../data/tests', 'incorrect path')
        self.assertEqual(fileext, 'csv', 'incorrect file extension')
        self.assertEqual(filepattern, 'test_eight_specimen_records', 
            'incorrect file pattern')

    def test_clean_header(self):
        header = ['b ', ' a', 'c	']
        result = clean_header(header)
        self.assertEqual(result, ['a', 'b', 'c'], 'header failed to be cleaned properly')

    def test_merge_headers(self):
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

if __name__ == '__main__':
    unittest.main()
