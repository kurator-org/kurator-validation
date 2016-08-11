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
__version__ = "dwca_utils.py 2016-08-04T16:01+02:00"

# This file contains common utility functions for dealing with the content of CSV and
# TXT data. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python dwca_utils.py

import os.path
import glob
import unittest
import re
import logging
import codecs
from slugify import slugify

try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    # jython pip install unicodecsv for use in workflows
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

ENCODINGS = ['utf_8', 'latin_1', 'ascii', 'cp1252', 'mac_roman', 'utf_16', 'big5', 
        'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp737', 'cp775', 'cp850', 
        'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 
        'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 
        'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 
        'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 
        'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 
        'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'iso8859_2', 
        'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 
        'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'johab', 
        'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 
        'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 
        'utf_16_be', 'utf_16_le', 'utf_7']

def setup_actor_logging(options):
    """Set up logging based on 'loglevel' in a dictionary.
    parameters:
        options - dictionary in which to look for loglevel (required)
    returns:
        None
    """
    try:
        loglevel = options['loglevel']
    except:
        loglevel = None
    if loglevel is not None:
        if loglevel.upper() == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
            logging.debug('Log level set to DEBUG')
        elif loglevel.upper() == 'INFO':        
            logging.basicConfig(level=logging.INFO)
            logging.info('Log level set to INFO')

def tsv_dialect():
    """Get a dialect object with tab-separated value properties.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with TSV attributes
    """
    dialect = csv.excel_tab
    dialect.lineterminator='\r'
    dialect.delimiter='\t'
    dialect.escapechar=''
    dialect.doublequote=True
    dialect.quotechar=''
    dialect.quoting=csv.QUOTE_NONE
    dialect.skipinitialspace=True
    dialect.strict=False
    return dialect
    
def csv_dialect():
    """Get a dialect object with CSV properties.
    parameters:
        None
    returns:
        dialect - a csv.dialect object with CSV attributes
    """
    dialect = csv.excel
    dialect.lineterminator='\r'
    dialect.delimiter=','
    dialect.escapechar='\\'
    dialect.doublequote=True
    dialect.quotechar='"'
    dialect.quoting=csv.QUOTE_MINIMAL
    dialect.skipinitialspace=True
    dialect.strict=False
    return dialect

def csv_file_dialect(fullpath):
    """Detect the dialect of a CSV or TXT data file.
    parameters:
        fullpath - full path to the file to process (required)
    returns:
        dialect - a csv.dialect object with the detected attributes
    """
    if fullpath is None or len(fullpath) == 0:
        logging.debug('No file given in csv_file_dialect().')
        return False

    # Cannot function without an actual file where full path points
    if os.path.isfile(fullpath) == False:
        logging.debug('File %s not found in csv_file_dialect().' % fullpath)
        return None

    # Let's look at up to readto bytes from the file
    readto = 4096
    filesize = os.path.getsize(fullpath)

    if filesize < readto:
        readto = filesize

    found_doublequotes = False
    with open(fullpath, 'rb') as file:
        # Try to read the specified part of the file
        try:
            buf = file.read(readto)
#            s = 'csv_file_dialect()'
#            s += ' buf:\n%s' % buf
#            logging.debug(s)
            # See if the buffer has any doubled double quotes in it. If so, infer that the 
            # dialect doublequote value should be true.
            if buf.find('""')>0:
                found_doublequotes = True
            # Make a determination based on existence of tabs in the buffer, as the
            # Sniffer is not particularly good at detecting TSV file formats. So, if the
            # buffer has a tab in it, let's treat it as a TSV file 
            if buf.find('\t')>0:
                return tsv_dialect()
#            dialect = csv.Sniffer().sniff(file.read(readto))
            # Otherwise let's see what we can find invoking the Sniffer.
            logging.debug('Forced to use csv.Sniffer()')
            dialect = csv.Sniffer().sniff(buf, delimiters=',\t|')
        except csv.Error:
            # Something went wrong, so let's try to read a few lines from the beginning of 
            # the file
            try:
                file.seek(0)
                s = 'csv_file_dialect()'
                s += ' Re-sniffing with tab to %s' % (readto)
                logging.debug(s)
                sample_text = ''.join(file.readline() for x in xrange(2,4,1))
                # See if the buffer has any doubled double quotes in it. If so, infer that the 
                # dialect doublequote value should be true.
                if sample_text.find('""')>0:
                    found_doublequotes = True
                dialect = csv.Sniffer().sniff(sample_text)
            # Sorry, couldn't figure it out
            except csv.Error:
                logging.debug('Unable to determine csv dialect')
                return None
    
    # Fill in some standard values for the remaining dialect attributes        
    if dialect.escapechar is None:
        dialect.escapechar='\\'

    dialect.skipinitialspace=True
    dialect.strict=False
    dialect.doublequote = found_doublequotes

    return dialect

def dialects_equal(dialect1, dialect2):
    ''' Determine if two dialects have the same attributes.
    parameters:
        dialect1 - a csv.dialect object (required)
        dialect2 - a csv.dialect object (required)
    returns:
        True is the attributes are all the same, otherwise False
    '''
    if dialect1 is None or dialect2 is None:
        return False
    if dialect1.lineterminator != dialect2.lineterminator:
        return False
    if dialect1.delimiter != dialect2.delimiter:
        return False
    if dialect1.escapechar != dialect2.escapechar:
        return False
    if dialect1.quotechar != dialect2.quotechar:
        return False
    if dialect1.doublequote != dialect2.doublequote:
        return False
    if dialect1.quoting != dialect2.quoting:
        return False
    if dialect1.skipinitialspace != dialect2.skipinitialspace:
        return False
    if dialect1.strict != dialect2.strict:
        return False
    return True

def dialect_attributes(dialect):
    ''' Get a string showing the attributes of a csv dialect.
    parameters:
        dialect - a csv.dialect object (required)
    '''
    if dialect is None:
        return 'No dialect given in dialect_attributes().'

    s = 'lineterminator: ' 

    if dialect.lineterminator == '\r':
        s+= '{CR}'
    elif dialect.lineterminator == '\n':
        s+= '{LF}'
    elif dialect.lineterminator == '\r\n':
        s+= '{CR}{LF}'
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
        fullpath - full path to the input file (required)
        dialect - csv.dialect object with the attributes of the input file (default None)
    returns:
        header - a list containing the fields in the original header
    """
    if fullpath is None or len(fullpath)==0:
        logging.debug('No file given in read_header().')
        return None

    # Cannot function without an actual file where the full path points
    if os.path.isfile(fullpath) == False:
        logging.debug('File %s not found in read_header().' % fullpath)
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

    return header

def composite_header(fullpath, dialect = None):
    """Get a header that includes all of the fields in headers of a set of files in the 
       given path.
    parameters:
        fullpath - full path to the files to process (required) (e.g., './*.txt')
        dialect - csv.dialect object with the attributes of the input files, which must
           all have the same dialect if dialect is given, otherwise it will be detected
           (default None)
    returns:
        compositeheader - a list containing the fields in the header
    """
    if fullpath is None or len(fullpath)==0:
        logging.debug('No file path given in composite_header().')
        return None

    compositeheader = None
    usedialect = dialect
    files = glob.glob(fullpath)

    if files is None:
        logging.debug('No files found on path %s in composite_header().' % fullpath)
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
        fullpath - full path to the input file (required)
        fieldnames -  list containing the fields in the header (required)
        dialect - csv.dialect object with the attributes of the output file (required)
    returns:
        True if the header was written to file, otherwise False
    """
    if fullpath is None or len(fullpath)==0:
        logging.debug('No output file given in write_header().')
        return False

    with open(fullpath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        try:
            writer.writeheader()
        except:
            s = 'No header written to output file %s in write_header().' % fullpath
            logging.debug(s)
            return False

    return True

def header_map(header):
    """Construct a map between a header and a cleaned version of the header.
    parameters:
        header - list of field names to clean (required)
    returns:
        headermap - a dictionary of cleanedfield:originalfield pairs
    """
    if header is None or len(header)==0:
        logging.debug('No header given in header_map().')
        return None

    headermap = {}

    for field in header:
        cleanfield = slugify(field)
        headermap[cleanfield]=field

    return headermap

def clean_header(header):
    """Construct a header from the cleaned field names in a header.
    parameters:
        header - list of field names (required)
    returns:
        cleanheader - a list of field names after cleaning
    """
    # Cannot function without a header
    if header is None or len(header)==0:
        logging.debug('No header given in clean_header().')
        return None

    cleanheader = []
    i=1

    # Clean each field in the header and append it to the cleanheader
    for field in header:
        cleanfield = slugify(field)
        if len(cleanfield)==0:
            cleanfield = 'field%s' % i

        cleanheader.append(cleanfield)
        i+=1

    return cleanheader

def merge_headers(headersofar, headertoadd = None):
    """Construct a header from the distinct white-space-stripped fields in two headers.
    parameters:
        headersofar - first header from which to build the composite (required)
        headertoadd -  a header to merge with the first header (optional)
    returns:
        a sorted list of fields for the combined header
    """
    if headersofar is None and headertoadd is None:
        logging.debug('No header given in merge_headers().')
        return None

    composedheader = set()

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
        logging.debug('No fields in composed header merge_headers().')
        return None

    return sorted(list(composedheader))

def csv_to_txt(inputfile, outputfile):
    """Convert an arbitrary csv file into a txt file.
    parameters:
        inputfile - full path to the input file (required)
        outputfile - full path to the converted file (required)
    returns:
        True if finished successfully, otherwise False
    """
    if inputfile is None or len(inputfile) == 0:
        logging.debug('No input file given in csv_to_txt().')
        return False

    if outputfile is None or len(outputfile) == 0:
        logging.debug('No output file given in csv_to_txt().')
        return False

    if os.path.isfile(inputfile) == False:
        logging.debug('File %s not found in csv_to_txt().' % inputfile)
        return False

    # Determine the dialect and encoding of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputencoding = csv_file_encoding(inputfile)
    inputheader = read_header(inputfile, inputdialect)
#    print 'inputdialect: %s' % dialect_attributes(inputdialect)
#    print 'inputencoding: %s' % inputencoding

    with open(outputfile, 'a') as tsvfile:
        writer = csv.DictWriter(tsvfile, dialect=tsv_dialect(), fieldnames=inputheader)
        writer.writeheader()
        for row in read_csv_row(inputfile, inputdialect, inputencoding):
#            print 'last row read successfully: %s' % row
            writer.writerow(row)

    return True

def term_rowcount_from_file(inputfile, termname):
    """Count of the rows that are populated for a given term.
    parameters:
        inputfile - full path to the input file (required)
        termname - term for which to count rows (required)
    returns:
        rowcount - the number of rows with the term populated
    """
    if inputfile is None or len(inputfile) == 0:
        logging.debug('No input file given in term_rowcount_from_file().')
        return 0

    if termname is None or len(termname) == 0:
        logging.debug('No term name given in term_rowcount_from_file().')
        return 0

    if os.path.isfile(inputfile) == False:
        logging.debug('File %s not found in term_rowcount_from_file().' % inputfile)
        return 0

    # Determine the dialect and encoding of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputencoding = csv_file_encoding(inputfile)
    inputheader = read_header(inputfile,inputdialect)

    if termname not in inputheader:
        logging.debug('Term %s not found in term_rowcount_from_file().' % termname)
        return 0

    rowcount = 0

    for row in read_csv_row(inputfile, inputdialect, inputencoding):
        try:
            value = row[termname]
            if value is not None and len(value.strip()) > 0:
                rowcount += 1
        except:
            pass

    return rowcount

def csv_field_checker(inputfile):
    """Determine if any row in a csv file has fewer fields than the header.
    parameters:
        inputfile - full path to the input file (required)
    returns:
        index, row - a tuple composed of the index of the first row that has a different 
            number of fields (1 is the first row after the header) and the row string
    """
    if inputfile is None or len(inputfile) == 0:
        logging.debug('No input file given in csv_field_checker().')
        return None

    if os.path.isfile(inputfile) == False:
        logging.debug('File %s not found in csv_field_checker().' % inputfile)
        return None

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    delimiter = inputdialect.delimiter
    header = read_header(inputfile,inputdialect)

    if header is None:
        return None

    fieldcount = len(header)

    with open(inputfile, 'rU') as f:
        i=0
        for line in f:
            delimitercount = line.count(delimiter)
            if delimitercount < fieldcount-1:
                return i, line
            i+=1

    return None

def csv_spurious_newline_condenser(inputfile, outputfile, sub='-'):
    """Remove new lines and carriage returns in data.
    parameters:
        inputfile - full path to the input file (required)
        outputfile - full path to the translated output file (required)
        sub - character sequence to substitute for the non-printing character 
            (default '-')
    returns:
        False if the removal does not complete successfully, otherwise True
    """
    if inputfile is None or len(inputfile) == 0:
        logging.debug('No input file given in csv_field_checker().')
        return None

    if os.path.isfile(inputfile) == False:
        logging.debug('File %s not found in csv_field_checker().' % inputfile)
        return None

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)
    delimiter = inputdialect.delimiter
    header = read_header(inputfile,inputdialect)

    if header is None:
        return None

    fieldcount = len(header)
    previousline = ''
    with open(outputfile, 'w') as outfile:
        with open(inputfile, 'rU') as infile:
            i = 0
            for line in infile:
                line = previousline.replace('\n',sub).replace('\r',sub) + line
                delimitercount = line.count(delimiter)
#                print 'line: %s (%s delimiter)' % (line, delimitercount)
                if delimitercount == fieldcount-1:
                    writethis = filter_non_printable(line,sub)
                    outfile.write(writethis)
#                    print 'writing line: %s' % writethis
                    previousline = ''
                elif delimitercount < fieldcount-1:
                    previousline = line
                else:
                    s = 'Unable to correctly join line %s from %s' % (i, inputfile)
                    logging.debug(s)
                    return False
                i += 1
    return True

def csv_file_encoding(inputfile):
    """Try to discern the encoding of a file.
    parameters:
        inputfile - the full path to an input file (required)
    returns:
        the best guess at an encoding
    """
    for e in ENCODINGS:
        try:
            fh = codecs.open(inputfile, 'r', encoding=e)
            fh.readlines()
            fh.seek(0)
        except UnicodeDecodeError:
            s = 'Encoding error with %s on file %s,' % (e, inputfile)
            s += ' trying different encoding'
            logging.debug(s)
        else:
            # Able to read the file in this encoding
            s = 'Encoding %s surmised for file %s,' % (e, inputfile)
            logging.debug(s)
            return e
    # Encoding not determined
    return None

def read_csv_row(fullpath, dialect, encoding):
    """Yield a row from a csv file. Determine the existence of the file, its dialect, and 
       its encoding before making a call to this function.
    parameters:
        fullpath - full path to the input file (required)
        dialect - csv.dialect object with the attributes of the input file (required)
        encoding - a string designating the input file encoding (required) 
            (e.g., 'utf_8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        row - the row as a dictionary
    """
    with open(fullpath, 'rU') as data:
        reader = csv.DictReader(utf8_data_encoder(data, encoding), dialect=dialect)
        for row in reader:
            # print '===row===:\n%s' % row
            for f in row:
                try:
                    row[f]=row[f].encode(encoding)
                except AttributeError, e:
                    s = 'Error encoding as %s: row[f]: %s' % (encoding, row[f])
                    logging.debug(s)
                    s = 'row: %s' % (row)
                    logging.debug(s)
            yield row

# def read_csv_row(fullpath, dialect, encoding):
#     """Yield a row from a csv file. Determine the existence of the file, its dialect, and 
#        its encoding before making a call to this function.
#     parameters:
#         fullpath - full path to the input file (required)
#         dialect - csv.dialect object with the attributes of the input file (required)
#         encoding - a string designating the input file encoding (required) 
#             (e.g., 'utf_8', 'mac_roman', 'latin_1', 'cp1252')
#     returns:
#         row - the row as a dictionary
#     """
#     with open(fullpath, 'rU') as data:
#         reader = csv.DictReader(data, dialect=dialect)
#         for row in reader:
#             # print '===row===:\n%s' % row
#             for f in row:
#                 try:
#                     row[f]=row[f].encode(encoding)
#                 except AttributeError, e:
#                     s = 'Error encoding as %s: row[f]: %s' % (encoding, row[f])
#                     logging.debug(s)
#                     s = 'row: %s' % (row)
#                     logging.debug(s)
#             yield row

def filter_non_printable(str, sub = ''):
    """Create a copy of a string with non-printing characters removed.
    parameters:
        str - the input string (required)
        sub - character sequence to substitute for the non-printing character 
            (default '')
    returns:
        string with the non-printing characters removed
    """
    newstr = ''
    for c in str:
        if ord(c) > 31 or ord(c) == 9 or ord(c) == 10 or ord(c) == 13:
            newstr += c
        else:
            newstr += sub
    return newstr

def file_filter_non_printable(inputfile, outputfile, sub = '-'):
    """Create a copy of a file with non-printing characters removed.
    parameters:
        inputfile - full path to the input file (required)
        outputfile - full path to the translated output file (required)
        sub - character sequence to substitute for the non-printing character 
            (default '-')
    returns:
        False if the translation does not complete successfully, otherwise True
    """
    i = 0
    with open(outputfile, 'w') as outdata:
        with open(inputfile, 'rU') as indata:
            for line in indata:
                try:
                    outdata.write( filter_non_printable(line, sub))
                except:
                    s = 'Failed to write line %s in %s. Aborting' % (i, inputfile)
                    logging.debug(s)
                    return False
                i += 1
    return True

def utf8_file_encoder(inputfile, outputfile, encoding=None):
    """Translate input file to utf8.
    parameters:
        inputfile - full path to the input file (required)
        outputfile - full path to the translated output file (required)
        encoding - encoding of the input file (optional)
    returns:
        False if the translation does not complete successfully, otherwise True
    """
    # Try to determine the encoding of the inputfile.
    if encoding is None or len(encoding.strip()) == 0 or encoding not in ENCODINGS:
        encoding = csv_file_encoding(inputfile)
    if encoding is None:
        # if we can't figure out the encoding, don't do anything.
        return None
    i = 0
    with open(outputfile, 'w') as outdata:
        with open(inputfile, 'rU') as indata:
            for line in indata:
                try:
                    outdata.write( utf8_line_encoder(line, encoding) )
                except UnicodeDecodeError, e:
                    s = 'Failed to encode line %s in %s. Aborting' % (i, encoding)
                    logging.debug(s)
                    return False
                i += 1
    return True

def utf8_data_encoder(data, encoding):
    """Yield a row in utf8 from a file in given encoding.
    parameters:
        data - the open input file (required)
        encoding - a string designating the input file encoding (required) 
            (e.g., 'utf_8', 'mac_roman', 'latin_1', 'cp1252')
    returns:
        the row in utf8
    """
    for line in data:
        try:
            yield utf8_line_encoder(line, encoding)
        except UnicodeDecodeError, e:
            print 'Failed to encode in encoding %s' % (encoding, e)

def utf8_line_encoder(line, encoding):
    """Get a row with a given encoding as utf8.
    parameters:
        line - the line to process (required)
        encoding - a string designating the input file encoding (required) 
            (e.g., 'utf_8', 'latin_1', 'cp1252')
    returns:
        the line in utf8
    """
    if encoding == 'utf_8':
        return line
    return line.decode(encoding).encode('utf_8')

def split_path(fullpath):
    """Parse out the path to, the name of, and the extension for a given file.
    parameters:
        fullpath - full path to the input file (required)
    returns:
        a tuple with the following elements:
            path - the path to the file (e.g., './')
            filext - the extension for the file name (e.g., 'thefile')
            filepattern - the file name without the path and extension (e.g., 'txt')
    """
    if fullpath is None or len(fullpath)==0:
        logging.debug('No input file given in split_path().')
        return None, None, None

    path = fullpath[:fullpath.rfind('/')]
    fileext = fullpath[fullpath.rfind('.')+1:]
    filepattern = fullpath[fullpath.rfind('/')+1:fullpath.rfind('.')]

    return path, fileext, filepattern

def response(returnvars, returnvals):
    """Create a dictionary combining keys with corresponding values.
    parameters:
        returnvars - keys to use in the output (required)
        returnvals - values for the keys in the output (required)
    returns:
        response - a dictionary of combined keys and values
    """
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
    non_printing_file = testdatapath + 'test_non-printing.csv'
    encodedfile_utf8 = testdatapath + 'test_eight_records_utf8_lf.csv'
    encodedfile_latin_1 = testdatapath + 'test_thirty_records_latin_1_crlf.csv'
    symbiotafile = testdatapath + 'test_symbiota_download.csv'
    csvreadheaderfile = testdatapath + 'test_eight_specimen_records.csv'
    tsvreadheaderfile = testdatapath + 'test_three_specimen_records.txt'
    tsvtest1 = testdatapath + 'test_tsv_1.txt'
    tsvtest2 = testdatapath + 'test_tsv_2.txt'
    csvtest1 = testdatapath + 'test_csv_1.csv'
    csvtest2 = testdatapath + 'test_csv_2.csv'
    csvtotsvfile1 = testdatapath + 'test_csv_1.csv'
    csvtotsvfile2 = testdatapath + 'test_csv_2.csv'
    monthvocabfile = testdatapath + 'test_vocab_month.txt'
    geogvocabfile = testdatapath + 'test_geography.txt'
    compositetestfile = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile1 = testdatapath + 'test_fieldcount.csv'
    fieldcountestfile2 = testdatapath + 'test_eight_specimen_records.csv'
    fieldcountestfile3 = testdatapath + 'test_bad_fieldcount1.txt'
    termrowcountfile1 = testdatapath + 'test_eight_specimen_records.csv'
    termrowcountfile2 = testdatapath + 'test_three_specimen_records.txt'
    termtokenfile = testdatapath + 'test_eight_specimen_records.csv'

    csvcompositepath = testdatapath + 'test_csv*.csv'
    tsvcompositepath = testdatapath + 'test_tsv*.txt'
    mixedcompositepath = testdatapath + 'test_*_specimen_records.*'

    # following are files output during the tests, remove these in dispose()
    csvwriteheaderfile = testdatapath + 'test_write_header_file.csv'
    tsvfromcsvfile1 = testdatapath + 'test_tsv_from_csv_1.txt'
    tsvfromcsvfile2 = testdatapath + 'test_tsv_from_csv_2.txt'
    testvocabfile = testdatapath + 'test_vocab_file.csv'
    testtokenreportfile = testdatapath + 'test_token_report_file.txt'
    testencoding = testdatapath + 'test_encoding.txt'
    testnonprinting = testdatapath + 'test_nonprinting_out.txt'
    newlinecondenser = testdatapath + 'test_newlinecondenser_out.txt'

    def dispose(self):
        csvwriteheaderfile = self.csvwriteheaderfile
        tsvfromcsvfile1 = self.tsvfromcsvfile1
        tsvfromcsvfile2 = self.tsvfromcsvfile2
        testvocabfile = self.testvocabfile
        testtokenreportfile = self.testtokenreportfile
        testencoding = self.testencoding
        testnonprinting = self.testnonprinting
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
        if os.path.isfile(testencoding):
            os.remove(testencoding)
        if os.path.isfile(testnonprinting):
            os.remove(testnonprinting)
#        if os.path.isfile(newlinecondenser):
#            os.remove(newlinecondenser)
        return True

class DWCAUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = DWCAUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        non_printing_file = self.framework.non_printing_file
        encodedfile_utf8 = self.framework.encodedfile_utf8
        encodedfile_latin_1 = self.framework.encodedfile_latin_1
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
        termrowcountfile1 = self.framework.termrowcountfile1
        termrowcountfile2 = self.framework.termrowcountfile2
        termtokenfile = self.framework.termtokenfile

        self.assertTrue(os.path.isfile(non_printing_file), non_printing_file + ' does not exist')
        self.assertTrue(os.path.isfile(encodedfile_utf8), encodedfile_utf8 + ' does not exist')
        self.assertTrue(os.path.isfile(encodedfile_latin_1), encodedfile_latin_1 + ' does not exist')
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
        self.assertTrue(os.path.isfile(termrowcountfile1), termrowcountfile1 + ' does not exist')
        self.assertTrue(os.path.isfile(termrowcountfile2), termrowcountfile2 + ' does not exist')
        self.assertTrue(os.path.isfile(termtokenfile), termtokenfile + ' does not exist')

    def test_tsv_dialect(self):
        print 'testing tsv_dialect'
        dialect = tsv_dialect()
        self.assertEqual(dialect.delimiter, '\t',
            'incorrect delimiter for tsv')
        self.assertEqual(dialect.lineterminator, '\r',
            'incorrect lineterminator for tsv')
        self.assertEqual(dialect.escapechar, '',
            'incorrect escapechar for tsv')
        self.assertEqual(dialect.quotechar, '',
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
        self.assertEqual(dialect.escapechar, '\\',
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
        self.assertEqual(dialect.escapechar, '',
            'incorrect escapechar for csv file')
        self.assertEqual(dialect.quotechar, '',
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
        expected = ['catalogNumber ', 'recordedBy', 'fieldNumber ', 'year', 'month', 
        'day', 'decimalLatitude ', 'decimalLongitude ', 'geodeticDatum ', 'country', 
        'stateProvince', 'county', 'locality', 'family ', 'scientificName ', 
        'scientificNameAuthorship ', 'reproductiveCondition ', 'InstitutionCode ', 
        'CollectionCode ', 'DatasetName ', 'Id']
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 21, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_read_header2(self):
        print 'testing read_header2'
        tsvheaderfile = self.framework.tsvtest1
        header = read_header(tsvheaderfile)
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', '']
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_read_header3(self):
        print 'testing read_header3'
        csvheaderfile = self.framework.csvtest1
        header = read_header(csvheaderfile)
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', '']
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_read_header4(self):
        print 'testing read_header4'
        tsvheaderfile = self.framework.tsvtest2
        header = read_header(tsvheaderfile)
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', 
        'decimalLatitude', 'decimalLongitude']
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_read_header5(self):
        print 'testing read_header5'
        csvheaderfile = self.framework.csvtest2
        header = read_header(csvheaderfile)
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', 
        'decimalLatitude', 'decimalLongitude']
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_read_header6(self):
        print 'testing read_header6'
        encodedfile_latin_1 = self.framework.encodedfile_latin_1
        header = read_header(encodedfile_latin_1)
        expected = ['id', 'class', 'coordinateUncertaintyInMeters', 'country',
            'eventDate', 'family', 'genus', 'decimalLatitude', 'decimalLongitude',
            'locality', 'scientificName', 'specificEpithet']
#        print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 12, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_composite_header(self):
        print 'testing composite_header'
        csvcompositepath = self.framework.csvcompositepath
        tsvcompositepath = self.framework.tsvcompositepath
        mixedcompositepath = self.framework.mixedcompositepath
        header = composite_header(csvcompositepath)
        expected = ['decimalLatitude', 'decimalLongitude', 'locality', 
        'materialSampleID', 'phylum', 'principalInvestigator']
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

#        header = composite_header(tsvcompositepath)
#        s =  'len(header)=%s' % len(header)
#        s += ' len(expected)=%s' % len(expected)
#        s += '\nheader:\n%s' % header
#        s += '\expected:\n%s' % expected
#        s += '\ntsvcompositepath: %s' % tsvcompositepath
#        print '%s' % s
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

        header = composite_header(mixedcompositepath)
        expected = ['BCID', 'CollectionCode', 'DatasetName', 'Id', 'InstitutionCode',
        'associatedMedia', 'associatedReferences', 'associatedSequences', 
        'associatedTaxa', 'basisOfIdentification', 'catalogNumber', 'class', 
        'coordinateUncertaintyInMeters', 'country', 'county', 'day', 'dayCollected',
        'dayIdentified', 'decimalLatitude', 'decimalLongitude', 'establishmentMeans', 
        'eventRemarks', 'extractionID', 'family', 'fieldNotes','fieldNumber', 
        'fundingSource', 'geneticTissueType', 'genus', 'geodeticDatum', 
        'georeferenceProtocol', 'habitat', 'identifiedBy', 'island', 'islandGroup', 
        'length', 'lifeStage', 'locality', 'materialSampleID', 'maximumDepthInMeters', 
        'maximumDistanceAboveSurfaceInMeters', 'microHabitat', 'minimumDepthInMeters', 
        'minimumDistanceAboveSurfaceInMeters', 'month', 'monthCollected', 
        'monthIdentified', 'occurrenceID', 'occurrenceRemarks', 'order', 
        'permitInformation', 'phylum', 'plateID', 'preservative', 
        'previousIdentifications', 'previousTissueID', 'principalInvestigator', 
        'recordedBy', 'reproductiveCondition', 'sampleOwnerInstitutionCode', 
        'samplingProtocol', 'scientificName', 'scientificNameAuthorship', 'sex', 
        'species', 'stateProvince', 'subSpecies', 'substratum', 'taxonRemarks', 
        'tissueStorageID', 'vernacularName', 'weight', 'wellID', 'wormsID', 'year', 
        'yearCollected', 'yearIdentified']
#        print 'len(header)=%s len(model)=%s\nheader:\n%smodel:\n\n%s' \
#            % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header),77, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

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
        s = 'header:\n%s\nnot as written header:\n%s' % (header, writtenheader)
        self.assertEqual(header, writtenheader, s)

    def test_dialect_preservation(self):
        print 'testing dialect preservation'
        csvreadheaderfile = self.framework.csvreadheaderfile
        csvwriteheaderfile = self.framework.csvwriteheaderfile
        indialect = csv_file_dialect(csvreadheaderfile)
        self.assertIsNotNone(indialect, 'input dialect not determined')

        header = read_header(csvreadheaderfile, indialect)
        self.assertIsNotNone(header, 'header not read')

        written = write_header(csvwriteheaderfile, header, indialect)
        self.assertTrue(written, 'header not written')

        outdialect = csv_file_dialect(csvwriteheaderfile)
        self.assertIsNotNone(header, 'output dialect not determined')
        equaldialects = dialects_equal(indialect, outdialect)
        if equaldialects == False:
            print 'input dialect:\n%s' % dialect_attributes(indialect)
            print 'output dialect:\n%s' % dialect_attributes(outdialect)
        self.assertTrue(equaldialects, 'input and output dialects not the same')

    def test_csv_to_txt1(self):
        print 'testing csv_to_txt1'
        csvfile = self.framework.csvtotsvfile1
        tsvfile = self.framework.tsvfromcsvfile1

        csv_to_txt(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv %s not written' % tsvfile)

        header = read_header(tsvfile)
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', '']
        # print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
        #    % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 5, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_csv_to_txt2(self):
        print 'testing csv_to_txt2'
        csvfile = self.framework.csvtotsvfile2
        tsvfile = self.framework.tsvfromcsvfile2

        csv_to_txt(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv %s not written' % tsvfile)

        header = read_header(tsvfile, tsv_dialect())
        expected = ['materialSampleID', 'principalInvestigator', 'locality', 'phylum', 
        'decimalLatitude', 'decimalLongitude']
        # print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
        #    % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 6, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_csv_to_txt3(self):
        print 'testing csv_to_txt3'
        csvfile = self.framework.encodedfile_latin_1
        tsvfile = self.framework.tsvfromcsvfile2

        csv_to_txt(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv %s not written' % tsvfile)

        header = read_header(tsvfile, tsv_dialect())
        expected = ['id','class','coordinateUncertaintyInMeters','country','eventDate',
            'family','genus','decimalLatitude','decimalLongitude','locality',
            'scientificName','specificEpithet']
        #print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
        #    % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 12, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

    def test_csv_to_txt4(self):
        print 'testing csv_to_txt4'
        csvfile = self.framework.symbiotafile
        tsvfile = self.framework.tsvfromcsvfile2

        csv_to_txt(csvfile, tsvfile)
        written = os.path.isfile(tsvfile)
        self.assertTrue(written, 'tsv %s not written' % tsvfile)

        header = read_header(tsvfile, tsv_dialect())
        expected = ['id', 'institutionCode', 'collectionCode', 'basisOfRecord', 
            'occurrenceID', 'catalogNumber', 'otherCatalogNumbers', 'kingdom', 'phylum',
            'class', 'order', 'family', 'scientificName', 'scientificNameAuthorship',
            'genus', 'specificEpithet', 'taxonRank', 'infraspecificEpithet',
            'identifiedBy', 'dateIdentified', 'identificationReferences', 
            'identificationRemarks', 'taxonRemarks', 'identificationQualifier',
            'typeStatus', 'recordedBy', 'recordedByID', 'associatedCollectors', 
            'recordNumber', 'eventDate', 'year', 'month', 'day', 'startDayOfYear',
            'endDayOfYear', 'verbatimEventDate', 'occurrenceRemarks', 'habitat', 
            'substrate', 'verbatimAttributes', 'fieldNumber', 'informationWithheld',
            'dataGeneralizations', 'dynamicProperties', 'associatedTaxa', 
            'reproductiveCondition', 'establishmentMeans', 'cultivationStatus', 
            'lifeStage', 'sex', 'individualCount', 'samplingProtocol', 'samplingEffort',
            'preparations', 'country', 'stateProvince', 'county', 'municipality', 
            'locality', 'locationRemarks', 'localitySecurity', 'localitySecurityReason',
            'decimalLatitude', 'decimalLongitude', 'geodeticDatum', 
            'coordinateUncertaintyInMeters', 'verbatimCoordinates', 'georeferencedBy',
            'georeferenceProtocol', 'georeferenceSources', 
            'georeferenceVerificationStatus', 'georeferenceRemarks', 
            'minimumElevationInMeters', 'maximumElevationInMeters', 
            'minimumDepthInMeters', 'maximumDepthInMeters', 'verbatimDepth', 
            'verbatimElevation', 'disposition', 'language', 'recordEnteredBy', 
            'modified', 'sourcePrimaryKey', 'collId', 'recordId', 'references']
        #print 'len(header)=%s len(model)=%s\nheader:\nmodel:\n%s\n%s' \
        #    % (len(header), len(modelheader), header, modelheader)
        self.assertEqual(len(header), 86, 'incorrect number of fields in header')
        s = 'header:\n%s\nnot as expected:\n%s' % (header, expected)
        self.assertEqual(header, expected, s)

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
        expected = ['b', 'a', 'c']
        self.assertEqual(result, expected, 'short header failed to be cleaned properly')

        header = ['catalogNumber ','recordedBy','fieldNumber ','year','month','day', \
            'decimalLatitude ','decimalLongitude ','geodeticDatum ','country', \
            'stateProvince','county','locality','family ','scientificName ', \
            'scientificNameAuthorship ','reproductiveCondition ','InstitutionCode ', \
            'CollectionCode ','DatasetName ','Id']
        result = clean_header(header)
        expected = ['catalognumber','recordedby','fieldnumber','year','month','day', \
            'decimallatitude','decimallongitude','geodeticdatum','country', \
            'stateprovince','county','locality','family','scientificname', \
            'scientificnameauthorship','reproductivecondition','institutioncode', \
            'collectioncode','datasetname','id']
#        print 'result: %s' % result
#        print 'expect: %s' % expected
        self.assertEqual(result, expected, 'long header failed to be cleaned properly')

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

        csvfile = self.framework.non_printing_file
        result = csv_field_checker(csvfile)
#        print 'csvfile: %s result: %s' % (csvfile, result)
        firstbadrow = result[0]
        s = 'field checker found first mismatched field in %s at row index %s'  \
            % (csvfile, firstbadrow)
        self.assertEqual(firstbadrow,5,s)

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

    def test_csv_file_encoding(self):
        print 'testing csv_file_encoding'
        encodedfile_utf8 = self.framework.encodedfile_utf8
        encodedfile_latin_1 = self.framework.encodedfile_latin_1
        
        encoding = csv_file_encoding(encodedfile_utf8)
        expected = 'utf_8'
        s = 'file encoding (%s) does not match expectation (%s)' % (encoding, expected)
        self.assertEqual(encoding,expected,s)
        
        encoding = csv_file_encoding(encodedfile_latin_1)
        expected = 'latin_1'
        s = 'file encoding (%s) does not match expectation (%s)' % (encoding, expected)
        self.assertEqual(encoding,expected,s)

    def test_utf8_file_encoder(self):
        print 'testing utf8_file_encoder'
        tempfile = self.framework.testencoding

        testfile = self.framework.encodedfile_utf8
        success = utf8_file_encoder(testfile, tempfile)
        s = '%s not translated to utf8' % testfile
        self.assertEqual(success,True,s)
        encoding = csv_file_encoding(tempfile)
        expected = 'utf_8'
        s = 'Encoding (%s) of %s to %s not utf_8' % (encoding, testfile, tempfile)
        self.assertEqual(encoding,expected,s)

        testfile = self.framework.encodedfile_latin_1
        success = utf8_file_encoder(testfile, tempfile)
        s = '%s not translated to utf8' % testfile
        self.assertEqual(success,True,s)
        encoding = csv_file_encoding(tempfile)
        expected = 'utf_8'
        s = 'Encoding (%s) of %s to %s not utf_8' % (encoding, testfile, tempfile)
        self.assertEqual(encoding,expected,s)

    def test_file_filter_non_printable(self):
        print 'testing file_filter_non_printable'
        testfile = self.framework.non_printing_file
        tempfile = self.framework.testnonprinting

        success = file_filter_non_printable(testfile, tempfile)
        s = 'Unable to remove non-printing characters from %s' % testfile
        self.assertEqual(success,True,s)

    def test_csv_spurious_newline_condenser(self):
        print 'testing csv_spurious_newline_condenser'
        testfile = self.framework.non_printing_file
        tempfile = self.framework.newlinecondenser

        success = csv_spurious_newline_condenser(testfile, tempfile)
        s = 'Unable to remove new lines from data content from %s' % testfile
        self.assertEqual(success,True,s)

if __name__ == '__main__':
    print '=== dwca_utils.py ==='
    unittest.main()
