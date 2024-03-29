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
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "report_utils.py 2017-07-20T10:38-07:00"
__kurator_content_type__ = "utility"
__adapted_from__ = ""

# This file contains common utility functions for dealing with the content of CSV and
# TSV data.

from dwca_utils import csv_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import csv_file_dialect
from dwca_utils import extract_values_from_row
from dwca_utils import get_guid
from dwca_utils import read_csv_row
from dwca_utils import read_header
from dwca_utils import strip_list
from dwca_utils import tsv_dialect
from dwca_utils import ustripstr
from dwca_utils import write_header
from dwca_vocab_utils import recommended_value
from dwca_vocab_utils import vocab_dict_from_file
from dwca_vocab_utils import vocabheader
import logging
import os.path

# Replace the system csv with unicodecsv. All invocations of csv will use unicodecsv,
# which supports reading and writing unicode streams.
try:
    import unicodecsv as csv
except ImportError:
    import warnings
    s = "The unicodecsv package is required.\n"
    s += "pip install unicodecsv\n"
    s += "$JYTHON_HOME/bin/pip install unicodecsv"
    warnings.warn(s)

def term_recommendation_report(
    reportfile, recommendationdict, key, separator=None, format=None):
    ''' Write a term recommendation report.
    parameters:
        reportfile - full path to the output report file (optional)
        recommendationdict - dictionary of term recommendations (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'term_recommendation_report()'

    if recommendationdict is None or len(recommendationdict)==0:
        s = 'No term recommendations given in %s.' % functionname
        logging.debug(s)
        return False

    if reportfile is None or len(reportfile)==0:
        s = 'No recommendation file name given in %s.' % functionname
        logging.debug(s)
        return False

    fieldnames = vocabheader(key, separator)

    if format is None or format.lower()=='csv':
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    # Create the outputfile and write the new header to it
    write_header(reportfile, fieldnames, dialect)

    if os.path.isfile(reportfile) == False:
        s = 'No header written to %s in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, encoding='utf-8', 
            fieldnames=fieldnames)
        for datakey, value in recommendationdict.iteritems():
            row = {key:datakey, 
                'standard':value['standard'], 
                'vetted':value['vetted'] }
            if separator is None:
                fields = [key]
            else:
                fields = key.split(separator)
            if len(fields) > 1:
                for field in fields:
                    row[field] = value[field]
            writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def term_list_report(reportfile, termlist, key, separator=None, format=None):
    ''' Write a report with a list of terms.
    parameters:
        reportfile - full path to the output report file (optional)
        termlist - list of terms to report (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
            in the vocabulary file (required)
        separator - string to use as the value separator in the string 
            (optional; default None)
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'term_list_report()'

    if termlist is None or len(termlist)==0:
        s = 'No term list given in %s.' % functionname
        logging.debug(s)
        return False

    if reportfile is None or len(reportfile)==0:
        s = 'No recommendation file name given in %s.' % functionname
        logging.debug(s)
        return False

    fieldnames = vocabheader(key, separator)

    if format is None or format.lower()=='csv':
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    # Create the outputfile and write the new header to it
    write_header(reportfile, fieldnames, dialect)

    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, encoding='utf-8', 
            fieldnames=fieldnames)
        for value in termlist:
            row = {key:value, 'standard':'', 'vetted':'0' }
            if separator is None:
                fields = [key]
            else:
                fields = key.split(separator)
            if len(fields) > 1:
                for field in fields:
                    row[field] = value
            writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def term_completeness_report(reportfile, fieldcountdict, format=None):
    ''' Write a report with a list of fields and the number of times they are populated.
    parameters:
        reportfile - full path to the output report file (optional)
        fieldcountdict - dictionary of field names and the number of rows in which they 
            are populated in the inputfile
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'term_completeness_report()'

    if fieldcountdict is None or len(fieldcountdict)==0:
        s = 'No field count dictionary given in %s.' % functionname
        logging.debug(s)
        return False

    if reportfile is None or len(reportfile)==0:
        s = 'No recommendation file name given in %s.' % functionname
        logging.debug(s)
        return False

    if format is None or format.lower()=='csv':
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    fields = []
    # Make an alphabetically sorted list of field names
    for key, value in fieldcountdict.iteritems():
        fields.append(key)
    fieldlist = sorted(fields)

    outputheader = ['field', 'count']
    # Create the outputfile and write the new header to it
    write_header(reportfile, outputheader, dialect)

    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, encoding='utf-8', 
            fieldnames=outputheader)
        for field in fieldlist:
            row = {'field':field , 'count':fieldcountdict[field] }
            writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def row_correct_term(row, fieldname, shouldbe):
    ''' In a row, update value of fieldname to value given by shouldbe and add field
        orig_fieldname with original value in the row.
    parameters:
        row - dictionary containing the row (required)
        fieldname - key in the dictionary for which to change the value (required)
        shouldbe - value to which to set the field (required)
    returns:
        row - row with substitutions and additions
    '''
    if row is None:
        return None

    if fieldname is None or len(fieldname.strip())==0:
        return row

    was = ''
    if fieldname in row:
        was = row[fieldname]

    row[fieldname] = shouldbe
    row[fieldname+'_orig'] = was

def term_setter_report(
    inputfile, reportfile, key, constantvalues=None, separator=None, encoding=None, 
    format=None):
    ''' Write a file substituting constants for fields that already exist in an input file 
        and with added fields with constants for fields that do not already exist in an 
       inputfile. Field name matching is exact.
    parameters:
        inputfile - full path to the input file (required)
        reportfile - full path to the output file (required)
        key - field or separator-separated fields to set (required)
        constantvalues - value or separator-separated values to set the field(s) to 
            (required)
        separator - string to use as the key and value separator (optional; default '|')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'term_setter_report()'

    if reportfile is None or len(reportfile)==0:
        s = 'No reportfile name given in %s.' % functionname
        logging.debug(s)
        return False

    if inputfile is None or len(inputfile) == 0:
        s = 'No inputfile file given in %s.' % functionname
        logging.debug(s)
        return False

    if os.path.isfile(inputfile) == False:
        s = 'Inputfile file %s not found in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Determine the dialect of the input file
    if encoding is None or len(encoding.strip()) == 0:
        encoding = csv_file_encoding(inputfile)

    # Read the header from the input file
    inputheader = read_header(inputfile, dialect=inputdialect, encoding=encoding)

    if inputheader is None:
        s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if key is None or len(key.strip())==0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return False

    if constantvalues is None or len(constantvalues)==0:
        s = 'No constantvalues given in %s.' % functionname
        logging.debug(s)
        return False

    # Make sure there is a separator for the next step
    if separator is None or len(separator)==0:
        separator = '|'

    # Get the fields to set by splitting the key with the separator
    fields = key.split(separator)

    # Get the values to set by splitting the constantvalues with the separator
    addedvalues = constantvalues.split(separator)

    # Abort if there is a mismatch in the lengths of the field and constants lists
    if len(fields) != len(addedvalues):
        s = 'length of field list: %s ' % key
        s += 'does not match length of constants list: %s ' % constantvalues
        s += 'in %s.' % functionname
        logging.debug(s)
        return False

    if  format is None or format.lower()=='txt':
        outputdialect = tsv_dialect()
    else:
        outputdialect = csv_dialect()

    # Make an outputheader that is a copy of the inputheader
    outputheader = inputheader

    # Add to the output header fields that are not in the inputheader
    for field in fields:
        if field not in outputheader:
            outputheader = outputheader + [field]

    # Create the outputfile and write the new header to it
    write_header(reportfile, outputheader, outputdialect)

    # Check to see if the outputfile was created
    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s was not created in %s.' % (outputfile, functionname)
        logging.debug(s)
        return False

    # Open the outputfile to append rows with fields set to constant values    
    with open(reportfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, encoding='utf-8', 
            fieldnames=outputheader)

        # Iterate through all rows in the input file
        for row in read_csv_row(inputfile, dialect=inputdialect, encoding=encoding, 
            header=True, fieldnames=inputheader):
            # For every field in the key list
            for i in range(0,len(fields)):
                # Set the value of the ith field to the ith constant
                row[fields[i]]=addedvalues[i]
            # Write the updated row to the outputfile
            writer.writerow(row)

    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def uuid_term_appender(
    inputfile, outputfile, key, guidtype=None, encoding=None, format=None):
    ''' Write a file adding a field populated by global unique identifiers (GUIDs) to the 
        fields in the input file.
    parameters:
        inputfile - full path to the input file (required)
        outputfile - full path to the output file (required)
        key - field or separator-separated fields to set (required)
        guidtype - type of GUID to use to populate the key (optional; default 'uuid')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'uuid_term_appender()'

    if outputfile is None or len(outputfile)==0:
        s = 'No outputfile name given in %s.' % functionname
        logging.debug(s)
        return False

    if inputfile is None or len(inputfile) == 0:
        s = 'No inputfile file given in %s.' % functionname
        logging.debug(s)
        return False

    if os.path.isfile(inputfile) == False:
        s = 'Inputfile file %s not found in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Determine the dialect of the input file
    if encoding is None or len(encoding.strip()) == 0:
        encoding = csv_file_encoding(inputfile)

    # Read the header from the input file
    inputheader = read_header(inputfile, dialect=inputdialect, encoding=encoding)

    if inputheader is None:
        s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if key is None or len(key.strip())==0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return False

    # Abort if the key exists in the inputheader
    if key in inputheader:
        s = 'field %s ' % key
        s += 'already exists in file %s ' % inputfile
        s += 'in %s.' % functionname
        logging.debug(s)
        return False

    if format is None or format.lower()=='txt':
        outputdialect = tsv_dialect()
    else:
        outputdialect = csv_dialect()

    # Make an outputheader that is a copy of the inputheader plus the new field to hold 
    # GUID.
    outputheader = inputheader + [key]

    # Create the outputfile and write the new header to it
    write_header(outputfile, outputheader, outputdialect)

    # Check to see if the outputfile was created
    if os.path.isfile(outputfile) == False:
        s = 'outputfile: %s was not created in %s.' % (outputfile, functionname)
        logging.debug(s)
        return False

    # Open the outputfile to append rows with appended GUID field  
    with open(outputfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, encoding='utf-8', 
            fieldnames=outputheader)

        # Iterate through all rows in the input file
        for row in read_csv_row(inputfile, dialect=inputdialect, encoding=encoding, 
            header=True, fieldnames=inputheader):
            # Create a GUID based on the selected guidtype
            guid = get_guid(guidtype)

            # Set the value of the key field to a GUID
            row[key]=guid

            # Write the updated row to the outputfile
            writer.writerow(row)

    s = 'Output file written to %s in %s.' % (outputfile, functionname)
    logging.debug(s)
    return True

def term_standardizer_report(
    inputfile, reportfile, vocabfile, key, separator=None, encoding=None, format=None):
    ''' Write a file with substitutions from a vocabfile for fields in a key and appended 
        terms showing the original values.
    parameters:
        inputfile - full path to the input file (required)
        reportfile - full path to the output file (required)
        vocabfile - path to the vocabulary file (required)
        key - field or separator-separated fields to set (required)
        separator - string to use as the key and value separator (optional; default '|')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    '''
    functionname = 'term_standardizer_report()'

    if reportfile is None or len(reportfile)==0:
        s = 'No reportfile name given in %s.' % functionname
        logging.debug(s)
        return False

    if inputfile is None or len(inputfile) == 0:
        s = 'No inputfile file given in %s.' % functionname
        logging.debug(s)
        return False

    if os.path.isfile(inputfile) == False:
        s = 'Inputfile file %s not found in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Determine the dialect of the input file
    if encoding is None or len(encoding.strip()) == 0:
        encoding = csv_file_encoding(inputfile)

    # Read the header from the input file
    inputheader = read_header(inputfile, dialect=inputdialect, encoding=encoding)

    if inputheader is None:
        s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if key is None or len(key.strip())==0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return False

    # Make sure there is a separator for the next step
    if separator is None or len(separator)==0:
        separator = '|'

    # Make a list of the fields in the key by splitting it on the separator
    fieldlist = key.split(separator)

    # Assume none of the fields is in the file
    headerhaskey = False

    # Search the cleaned up header for any field from the key
    cleanedinputheader = strip_list(inputheader)
    for field in fieldlist:
       if field in cleanedinputheader:
           headerhaskey = True
           break

    if headerhaskey == False:
        s = 'No field from %s found ' % fieldlist
        s += 'in input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if vocabfile is None or len(vocabfile) == 0:
        logging.debug('No vocabulary file given in %s.') % functionname
        return False

    if os.path.isfile(vocabfile) == False:
        s = 'Vocabulary file %s not found in %s.' % (vocabfile, functionname)
        logging.debug(s)
        return False

    # Get the vocabulary dictionary, but convert all entries using ustripstr. Assume
    # vocabulary file is encoded as utf-8.
    vocabdict = vocab_dict_from_file(vocabfile, key, encoding='utf-8', \
        separator=separator, function=ustripstr)
    if len(vocabdict) == 0:
        s = 'Vocabulary file %s ' % vocabfile
        s += 'had zero recommendations in %s.' % functionname
        logging.debug(s)
        return False

    if format is None or format.lower()=='txt':
        dialect = tsv_dialect()
    else:
        dialect = csv_dialect()

    if format is None or format.lower()=='txt':
        outputdialect = tsv_dialect()
    else:
        outputdialect = csv_dialect()

    # Create an output header that is the same as the input header with fields
    # appended to hold the original values of the key fields
    # Get the fields to add by splitting the key with the separator
    outputheader = cleanedinputheader
    for field in fieldlist:
        if field in outputheader:
            outputheader = outputheader + [field+'_orig']
        else:
            outputheader = outputheader + [field]

    # Create the outputfile and write the new header to it
    write_header(reportfile, outputheader, outputdialect)

    # Check to see if the outputfile was created
    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    # Open the outputfile to append rows having the added fields
    with open(reportfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, encoding='utf-8', 
            fieldnames=outputheader)
        # Iterate through all rows in the input file
        for row in read_csv_row(inputfile, dialect=inputdialect, encoding=encoding, 
            header=True, fieldnames=cleanedinputheader):
            # Set the _orig values for every field in the field list that exists in
            # the row
            for field in fieldlist:
                if field in row:
                    row[field+'_orig'] = row[field]

            # Construct a composite field value for the row to match a key in the 
            # vocabulary file
            rowkey = extract_values_from_row(row, fieldlist, separator)

            # Get dictionary for recommended value for the ustripstr(rowkey)
            newvaluedict = recommended_value(vocabdict, ustripstr(rowkey))

            # Only make changes if there is a standardized value found
            if newvaluedict is not None:
                # ustripstr(rowkey) was found in the vocabulary
                # Get the standard value
                standard = newvaluedict['standard']

                # Treat standard value that is None or only whitespace as ''
                if standard is None or len(standard.strip())==0:
                    standard=''

                # Make a list of values given in standard
                newvalues = standard.split(separator)

                # Only make changes if the number of recommendation fields is the 
                # same as the number of fields in the key
                if len(newvalues) == len(fieldlist):
                    i = 0
                    # Update or add new value to field in the fieldlist
                    for field in fieldlist:
                        row[field] = newvalues[i]
                        i += 1

            writer.writerow(row)

    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True    
