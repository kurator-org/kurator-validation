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
__copyright__ = "Copyright 2015 President and Fellows of Harvard College"
__version__ = "dwca_utils.py 2015-12-30T20:16-03:00"

import os.path
import csv
import glob
import unittest

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
    
def read_header(fullpath, dialect = None):
    """Get the header line of a CSV or TXT data file.
    parameters:
        fullpath - the full path to the file to process.
        dialect - a csv.dialect object with the attributes of the input file
    returns:
        cleanheader - a list object containing the white-space-free fields in the 
            original header"""
    header = None
    if dialect is None:
        dialect = csv_file_dialect(fullpath)
    with open(fullpath, 'rU') as csvfile:
        reader = csv.DictReader(csvfile, dialect=dialect)
        # header is the list as returned by the reader
        header=reader.fieldnames

        # cleanheader is header with any extraneous whitespace in field names removed
        cleanheader = []
        for field in header:
            cleanheader.append(field.strip())
    return cleanheader

def write_header(fullpath, fieldnames, dialect):
    """Write the header line of a CSV or TXT data file.
    parameters:
        fullpath - the full path to the file to process.
        fieldnames -  a list object containing the fields in the header
        dialect - a csv.dialect object with the attributes of the input file
    returns:
        success - True is the header was written to file"""
    success = False
    with open(fullpath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        writer.writeheader()
        success = True
    return success

def compose_header(fullpath, headersofar = None, dialect = None):
    """Compose a header that includes all of the fields in given header plus the fields 
       in a given data file.
    parameters:
        fullpath - the full path to the file to process. (e.g., '../../data/filewithheader.txt')
        headersofar - a list containing the fields composed so far
        dialect - a csv.dialect object with the attributes of the input file.
    returns:
        sorted(list(composedheader)) - a list object containing the fields in the 
            combined header"""
    if fullpath is None:
        return headersofar
    composedheader = set()
    if headersofar is not None:
        for field in headersofar:
            composedheader.add(field)
        
    if dialect is None:
        dialect = csv_file_dialect(fullpath)
    header = read_header(fullpath, dialect)
    for field in header:
        composedheader.add(field)
    return sorted(list(composedheader))

def composite_header(fullpath, dialect = None):
    """Get a header line that includes all of the fields in headers of a set of CSV 
       or TXT data files.
    parameters:
        fullpath - the full path to the files to process. (e.g., './*.txt')
        dialect - a csv.dialect object with the attributes of the input files, which must 
           all have the same dialect if dialect is given, otherwise it will be detected.
    returns:
        sorted(list(compositeheader)) - a list object containing the fields in the 
            header"""
    if fullpath is None:
        return None
    compositeheader = set()
    usedialect = dialect
    files = glob.glob(fullpath)
    if files is None:
        return None
    for file in files:
        if dialect is None:
            print 'file: %s dialect: %s' % (file, dialect)
            usedialect = csv_file_dialect(file)
        header = read_header(file, usedialect)
        for field in header:
            compositeheader.add(field)
    if '' in compositeheader:
        compositeheader.remove('')
    return sorted(list(compositeheader))

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

class DWCAUtilsFramework():
    testdatapath = '../../data/tests/'
    csvreadheaderfile = 'test_eight_specimen_records.csv'
    csvwriteheaderfile = 'test_write_header_file.csv'
    compositeheaderfilepattern = 'test_compositeheader'
    compositeheaderfilepattern2 = 'test_compositeheader_2'
    tsvdialecttestfile = 'test_fims_6e4532.txt'
    fimstest1 = 'test_fims_6e4532.tst'
    fimstest2 = 'test_fims_6e5432.tst'
    aggregatetest = 'test_aggregate.txt'

    def dispose(self):
        testdatapath = self.testdatapath
        compositeheaderfilepattern = self.compositeheaderfilepattern
        compositeheaderfilepattern2 = self.compositeheaderfilepattern2
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvdialecttestfile = self.tsvdialecttestfile
        fimstest1 = self.fimstest1
        fimstest2 = self.fimstest2
        aggregatetest = self.aggregatetest
        
        if os.path.isfile(testdatapath + csvwriteheaderfile):
            os.remove(testdatapath + csvwriteheaderfile)
        files = glob.glob(testdatapath + compositeheaderfilepattern + '*')
        for file in files:
            os.remove(file)
        files = glob.glob(testdatapath + compositeheaderfilepattern2 + '*')
        for file in files:
            os.remove(file)
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

    def test_csv_file_dialect(self):
        testdatapath = self.framework.testdatapath
        csvreadheaderfile = self.framework.csvreadheaderfile
        tsvfile = self.framework.tsvdialecttestfile

        dialect = csv_file_dialect(testdatapath + tsvfile)

        self.assertIsNotNone(dialect, 'unable to detect tsv file dialect')

        dialect = csv_file_dialect(testdatapath + csvreadheaderfile)

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

    def test_read_header(self):
        testdatapath = self.framework.testdatapath
        csvreadheaderfile = self.framework.csvreadheaderfile

        header = read_header(testdatapath + csvreadheaderfile)
        modelheader = []
        modelheader.append('catalogNumber')
        modelheader.append('recordedBy')
        modelheader.append('fieldNumber')
        modelheader.append('year')
        modelheader.append('month')
        modelheader.append('day')
        modelheader.append('decimalLatitude')
        modelheader.append('decimalLongitude')
        modelheader.append('geodeticDatum')
        modelheader.append('country')
        modelheader.append('stateProvince')
        modelheader.append('county')
        modelheader.append('locality')
        modelheader.append('family')
        modelheader.append('scientificName')
        modelheader.append('scientificNameAuthorship')
        modelheader.append('reproductiveCondition')
        modelheader.append('InstitutionCode')
        modelheader.append('CollectionCode')
        modelheader.append('DatasetName')
        modelheader.append('Id')

        self.assertEqual(len(header), 21, 'incorrect number of fields in header')
        self.assertEqual(header, modelheader, 'header not equal to the model header')

    def test_write_header(self):
        testdatapath = self.framework.testdatapath
        csvreadheaderfile = self.framework.csvreadheaderfile
        csvwriteheaderfile = self.framework.csvwriteheaderfile

        header = read_header(testdatapath + csvreadheaderfile)
        dialect = tsv_dialect()

        self.assertIsNotNone(header, 'model header not found')
        written = write_header(testdatapath + csvwriteheaderfile, header, dialect)

        self.assertTrue(written, 'header not written to csvwriteheaderfile')

        writtenheader = read_header(testdatapath + csvwriteheaderfile)

        self.assertEqual(len(header), len(writtenheader),
            'incorrect number of fields in writtenheader')

        self.assertEqual(header, writtenheader,
            'writtenheader not the same as model header')
        
    def test_split_path(self):
        path, fileext, filepattern = \
            split_path('../../data/tests/test_eight_specimen_records.csv')
        self.assertEqual(path, '../../data/tests', 'incorrect path')
        self.assertEqual(fileext, 'csv', 'incorrect file extension')
        self.assertEqual(filepattern, 'test_eight_specimen_records', 
            'incorrect file pattern')

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

    def test_compose_header(self):
        testdatapath = self.framework.testdatapath
        csvreadheaderfile = self.framework.csvreadheaderfile

        headersofar = ['extrafield1', 'extrafield2']

        composedheader = compose_header(testdatapath + csvreadheaderfile, headersofar)

        self.assertEqual(len(composedheader), 23,
            'incorrect number of fields in composedheader')

    def test_composite_header2(self):
        testdatapath = self.framework.testdatapath
        compositeheaderfilepattern = self.framework.compositeheaderfilepattern2
        tsv = tsv_dialect()
        f1 = 'test_fims_6e4532.tst'
        f2 = 'test_fims_6e5432.tst'
        h1 = read_header(testdatapath + f1)
        h2 = read_header(testdatapath + f2, tsv)
        written = write_header(testdatapath + compositeheaderfilepattern + '1.tsv', 
            h1, tsv)

        self.assertTrue(written, 'h1 not written')

        written = write_header(testdatapath + compositeheaderfilepattern + '2.tsv', 
            h2, tsv)

        self.assertTrue(written, 'h2 not written')

        h3 = composite_header(testdatapath + compositeheaderfilepattern + '*')
        
        print 'h1:\n%s' % h1
        print 'h2:\n%s' % h2
        print 'h3:\n%s' % h3

        destfile = testdatapath + 'test_aggregate.txt'
        with open(destfile, 'w') as outfile:
            writer = csv.DictWriter(outfile, dialect=tsv_dialect(), 
                fieldnames=h3, extrasaction='ignore')
            writer.writeheader()
            files = glob.glob(testdatapath + 'test_fims_6e*.tst')
            for file in files:
                print 'file: %s' % (file)
                with open(file, 'rU') as inputfile:
                    reader = csv.DictReader(inputfile, dialect=tsv_dialect())
                    for line in reader:
                        print 'line:\n%s' % line
                        writer.writerow(line)
#                         try:
#                             writer.writerow(line)
#                         except:
#                             print 'line:\n%s' % line


    def test_composite_header(self):
        testdatapath = self.framework.testdatapath
        compositeheaderfilepattern = self.framework.compositeheaderfilepattern
        header1 = ['a', 'b', 'c']
        header2 = ['b', 'c', 'd']
        header3 = ['a', 'd', 'e']
        expectedheader = ['a', 'b', 'c', 'd', 'e']
        
        dialect1 = tsv_dialect()
        dialect2 = csv.excel
        dialect3 = csv.excel_tab

        written = write_header(testdatapath + compositeheaderfilepattern + '1.tsv', 
            header1, dialect1)

        self.assertTrue(written, 'header1 not written')

        written = write_header(testdatapath + compositeheaderfilepattern + '2.csv', 
            header2, dialect2)

        self.assertTrue(written, 'header2 not written')

        written = write_header(testdatapath + compositeheaderfilepattern + '3.tsv', 
            header3, dialect3)

        self.assertTrue(written, 'header3 not written')

        observedheader = composite_header(testdatapath + compositeheaderfilepattern + '*')

        self.assertEqual(expectedheader, observedheader,
            'observedheader not the same as expected header')

if __name__ == '__main__':
    """Test of dwca_utils functions"""
    unittest.main()
