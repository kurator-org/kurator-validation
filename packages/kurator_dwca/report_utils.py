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
__version__ = "report_utils.py 2016-09-26T16:05+02:00"

# This file contains common utility functions for dealing with the content of CSV and
# TSV data. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python report_utils.py

from dwca_utils import csv_dialect
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import ustripstr
from dwca_utils import strip_list
from dwca_utils import read_header
from dwca_terms import vocabfieldlist
from dwca_utils import extract_values_from_row
from dwca_vocab_utils import vocabheader
from dwca_vocab_utils import recommended_value
from dwca_vocab_utils import vocab_dict_from_file
import logging
import unittest
import os.path
try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

def term_recommendation_report(reportfile, recommendationdict, key, separator='|', 
    format=None):
    """Write a term recommendation report.
    parameters:
        reportfile - full path to the output report file (optional)
        recommendationdict - dictionary of term recommendations (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        success - True if the report was written, else False
    """
    functionname = 'term_recommendation_report()'
#    print 'reportfile: %s\nrecommendationdict: %s' % (reportfile, recommendationdict)
    if recommendationdict is None or len(recommendationdict)==0:
        s = 'No term recommendations given in %s.' % functionname
        logging.debug(s)
        return False

    if reportfile is None or len(reportfile)==0:
        s = 'No recommendation file name given in %s.' % functionname
        logging.debug(s)
        return False

    fieldnames = vocabheader(key, separator)

    if format=='csv' or format is None:
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        writer.writeheader()

    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        for datakey, value in recommendationdict.iteritems():
            row = {key:datakey, 
                'standard':value['standard'], 
                'vetted':value['vetted'] }
            fields = key.split(separator)
            if len(fields) > 1:
                for field in fields:
                    row[field] = value[field]
            writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def term_list_report(reportfile, termlist, key, separator='|', format=None):
    """Write a report with a list of terms.
    parameters:
        reportfile - full path to the output report file (optional)
        termlist - list of terms to report (required)
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
    returns:
        success - True if the report was written, else False
    """
    functionname = 'term_list_report()'
#    print 'reportfile: %s\term_list_report: %s' % (reportfile, term_list_report)
    if termlist is None or len(termlist)==0:
        s = 'No term list given in %s.' % functionname
        logging.debug(s)
        return False

    if reportfile is None or len(reportfile)==0:
        s = 'No recommendation file name given in %s.' % functionname
        logging.debug(s)
        return False

    fieldnames = vocabheader(key, separator)

    if format=='csv' or format is None:
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        writer.writeheader()

    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=fieldnames)
        for value in termlist:
            row = {key:value, 'standard':'', 'vetted':'0' }
            fields = key.split(separator)
            if len(fields) > 1:
                # print 'report row: %s' % row
                # print 'fields: %s' % fields
                for field in fields:
                    row[field] = value
            writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def row_correct_term(row, fieldname, shouldbe):
    """In a row, update value of fieldname to value given by shouldbe and add field
       orig_fieldname with original value in the row.
    parameters:
        row - dictionary containing the row (required)
        fieldname - key in the dictionary for which to change the value (required)
        shouldbe - value to which to set the field (required)
    returns:
        row - row with substitutions and additions
    """
    if row is None:
        return None
    if fieldname is None or len(fieldname.strip())==0:
        return row
    was = ''
    if fieldname in row:
        was = row[fieldname]
    row[fieldname] = shouldbe
    row[fieldname+'_orig'] = was

def term_setter_report(inputfile, reportfile, key, constantvalues=None, separator='|', \
    format=None):
    """Write a file substituting constants for fields that already exist in an input file 
       and with added fields with constants for fields that do not already exist in an 
       inputfile. Field name matching is exact.
    parameters:
        inputfile - full path to the input file (required)
        reportfile - full path to the output file (required)
        key - field or separator-separated fields to set (required)
        constantvalues - value or separator-separated values to set the field(s) to 
            (required)
        separator - string to use as the key and value separator (optional; default '|')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    """
    functionname = 'term_setter_report()'
    ### Required parameters ###
    if reportfile is None or len(reportfile)==0:
        s = 'No reportfile name given in %s.' % functionname
        logging.debug(s)
        return False

    # Read the header from the input file
    inputheader = read_header(inputfile)
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

    ### Optional parameters ###
    if format=='txt' or format is None:
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
    with open(reportfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        writer.writeheader()

    # Check to see if the outputfile was created
    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s was not created in %s.' % (outputfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Open the outputfile to append rows with fields set to constant values    
    with open(reportfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        # Open the inputfile to read rows
        with open(inputfile, 'rU') as infile:
            dr = csv.DictReader(infile, dialect=inputdialect, fieldnames=inputheader)
            # Read the header
            dr.next()
            # Read every row in the inputfile
            for row in dr:
                # For every field in the key list
                for i in range(0,len(fields)):
                    # Set the value of the ith field to the ith constant
                    row[fields[i]]=addedvalues[i]
                # Write the updated row to the outputfile
                writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

def term_standardizer_report(inputfile, reportfile, vocabfile, key, separator='|', 
    format=None):
    """Write a file with substitutions from a vocabfile for fields in a key and appended 
       terms showing the original values.
    parameters:
        inputfile - full path to the input file (required)
        reportfile - full path to the output file (required)
        vocabfile - path to the vocabulary file (required)
        key - field or separator-separated fields to set (required)
        separator - string to use as the key and value separator (optional; default '|')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    """
    functionname = 'term_standardizer_report()'
    ### Required parameters ###
    if reportfile is None or len(reportfile)==0:
        s = 'No reportfile name given in %s.' % functionname
        logging.debug(s)
        return False

    # Read the header from the input file
    inputheader = read_header(inputfile)
    if inputheader is None:
        s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if key is None or len(key.strip())==0:
        s = 'No key given in %s.' % functionname
        logging.debug(s)
        return False

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

    # Get the vocabulary dictionary, but convert all entries using ustripstr
    vocabdict = vocab_dict_from_file(vocabfile, key, function=ustripstr)
    if len(vocabdict) == 0:
        s = 'Vocabulary file %s ' % vocabfile
        s += 'had zero recommendations in %s.' % functionname
        logging.debug(s)
        return False

    if format=='txt' or format is None:
        dialect = tsv_dialect()
    else:
        dialect = csv_dialect()

    ### Optional parameters ###
    if format=='txt' or format is None:
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
    with open(reportfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        writer.writeheader()

    # Check to see if the outputfile was created
    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Open the outputfile to append rows having the added fields
    with open(reportfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        # Open the inputfile to read rows
        with open(inputfile, 'rU') as infile:
            dr = csv.DictReader(infile,dialect=inputdialect,fieldnames=cleanedinputheader)
            # Read the header
            dr.next()
            # Read every row in the inputfile
            for row in dr:
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

# def term_standardizer_report(inputfile, reportfile, vocabfile, key, separator='|', 
#     format=None):
#     """Write a file with substitutions for a given term based on the vocabfile and 
#        an appended term showing the original value.
#     parameters:
#         inputfile - full path to the input file (required)
#         reportfile - full path to the output file (required)
#         vocabfile - path to the vocabulary file (required)
#         key - field or separator-separated fields to set (required)
#         separator - string to use as the key and value separator (optional; default '|')
#         format - string signifying the csv.dialect of the report file ('csv' or 'txt')
#             (optional; default: txt)
#     returns:
#         success - True if the report was written, else False
#     """
#     functionname = 'term_standardizer_report()'
#     ### Required parameters ###
#     if reportfile is None or len(reportfile)==0:
#         s = 'No reportfile name given in %s.' % functionname
#         logging.debug(s)
#         return False
# 
#     # Read the header from the input file
#     inputheader = read_header(inputfile)
#     if inputheader is None:
#         s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
#         logging.debug(s)
#         return False
# 
#     if key is None or len(key.strip())==0:
#         s = 'No key given in %s.' % functionname
#         logging.debug(s)
#         return False
# 
#     if key not in inputheader:
#         s = 'Key %s not found in input file %s in %s.' % (key, inputfile, functionname)
#         logging.debug(s)
#         return False
# 
#     if vocabfile is None or len(vocabfile) == 0:
#         logging.debug('No vocabulary file given in %s.') % functionname
#         return False
# 
#     if os.path.isfile(vocabfile) == False:
#         s = 'Vocabulary file %s not found in %s.' % (vocabfile, functionname)
#         logging.debug(s)
#         return False
# 
#     # Get the vocabulary dictionary, but convert all entries using ustripstr
#     vocabdict = vocab_dict_from_file(vocabfile, key, function=ustripstr)
#     if len(vocabdict) == 0:
#         s = 'Vocabulary file %s ' % vocabfile
#         s += 'had zero recommendations in %s.' % functionname
#         logging.debug(s)
#         return False
# 
#     if format=='txt' or format is None:
#         dialect = tsv_dialect()
#     else:
#         dialect = csv_dialect()
# 
#     ### Optional parameters ###
#     if format=='txt' or format is None:
#         outputdialect = tsv_dialect()
#     else:
#         outputdialect = csv_dialect()
# 
#     # Create an output header that is the same as the input header with a field
#     # appended to hold the original value of the key field
#     addedfield = key+'_orig'
#     outputheader = inputheader + [addedfield]
# 
#     # Create the outputfile and write the new header to it
#     with open(reportfile, 'w') as outfile:
#         writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
#         writer.writeheader()
# 
#     # Check to see if the outputfile was created
#     if os.path.isfile(reportfile) == False:
#         s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
#         logging.debug(s)
#         return False
# 
#     # Determine the dialect of the input file
#     inputdialect = csv_file_dialect(inputfile)
# 
#     # Open the outputfile to append rows having the added fields
#     with open(reportfile, 'a') as outfile:
#         writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
#         # Open the inputfile to read rows
#         with open(inputfile, 'rU') as infile:
#             dr = csv.DictReader(infile, dialect=inputdialect, fieldnames=inputheader)
#             # Read the header
#             dr.next()
#             # Read every row in the inputfile
#             for row in dr:
#                 # Get the recommended value for the ustripstr'd original value of the 
#                 # key field
#                 newvalue = recommended_value(vocabdict, ustripstr(row[key]))
#                 # Add the field for the original value of the  key
#                 row[addedfield] = row[key]
#                 if newvalue is not None and 'standard' in newvalue:
#                     # Set the value of the key field to the looked up value
#                     row[key] = newvalue['standard']
#                 writer.writerow(row)
#     s = 'Report written to %s in %s.' % (reportfile, functionname)
#     logging.debug(s)
#     return True

def termlist_corrector_report(inputfile, reportfile, vocabdirectory, fieldlist, key, 
    separator='|', format=None):
    """Specialized function with assumptions about the vocabulary files. Write a file 
       with substitutions for a list of terms based on the vocabulary files in the given 
       vocabdirectory that match the field names + '.txt'. Appended terms showing the 
       original values.
    parameters:
        inputfile - full path to the input file (required)
        reportfile - full path to the output file (required)
        vocabdirectory - path to the directory where the vocabulary files are located
            (optional; default '')
        key - field or separator-separated fields to set (required)
        separator - string to use as the key and value separator (optional; default '|')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
            (optional; default: txt)
    returns:
        success - True if the report was written, else False
    """
    functionname = 'termlist_corrector_report()'
    ### Required parameters ###
    if reportfile is None or len(reportfile)==0:
        s = 'No reportfile name given in %s.' % functionname
        logging.debug(s)
        return False

    # Read the header from the input file
    inputheader = read_header(inputfile)
    if inputheader is None:
        s = 'Unable to read header from input file %s in %s.' % (inputfile, functionname)
        logging.debug(s)
        return False

    if key is None or len(key.strip())==0:
        s = 'No key given in %s().'
        logging.debug(s)
        return False

    if key not in inputheader:
        s = 'Key %s not found in input file %s in %s.' % (key, inputfile, functionname)
        logging.debug(s)
        return False

    if vocabfile is None or len(vocabfile) == 0:
        s = 'No vocabulary file given in %s.' % functionname
        logging.debug(s)
        return False

    if os.path.isfile(vocabfile) == False:
        s = 'Vocabulary file %s not found in %s.' % (vocabfile, functionname)
        logging.debug(s)
        return False

    # Get the vocabulary dictionary, but convert all entries using ustripstr
    vocabdict = vocab_dict_from_file(vocabfile, key, function=ustripstr)
    if len(vocabdict) == 0:
        s = 'Vocabulary file %s ' % vocabfile
        s += 'had zero recommendations in %s.' % functionname
        logging.debug(s)
        return False

    if format=='txt' or format is None:
        dialect = tsv_dialect()
    else:
        dialect = csv_dialect()

    ### Optional parameters ###
    if format=='txt' or format is None:
        outputdialect = tsv_dialect()
    else:
        outputdialect = csv_dialect()

    # Create an output header that is the same as the input header with a field
    # appended to hold the original value of the key field
    addedfield = key+'_orig'
    outputheader = inputheader + [addedfield]

    # Create the outputfile and write the new header to it
    with open(reportfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        writer.writeheader()

    # Check to see if the outputfile was created
    if os.path.isfile(reportfile) == False:
        s = 'reportfile: %s not created in %s.' % (reportfile, functionname)
        logging.debug(s)
        return False

    # Determine the dialect of the input file
    inputdialect = csv_file_dialect(inputfile)

    # Open the outputfile to append rows having the added fields
    with open(reportfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, fieldnames=outputheader)
        # Open the inputfile to read rows
        with open(inputfile, 'rU') as infile:
            dr = csv.DictReader(infile, dialect=inputdialect, fieldnames=inputheader)
            # Read the header
            dr.next()
            # Read every row in the inputfile
            for row in dr:
                # Get the recommended value for the ustripstr'd original value of the 
                # key field
                newvalue = recommended_value(vocabdict, ustripstr(row[key]))
                # Add the field for the original value of the  key
                row[addedfield] = row[key]
                if newvalue is not None and 'standard' in newvalue:
                    # Set the value of the key field to the looked up value
                    row[key] = newvalue['standard']
                writer.writerow(row)
    s = 'Report written to %s in %s.' % (reportfile, functionname)
    logging.debug(s)
    return True

class ReportUtilsFramework():
    # testdatapath is the location of the files to test with
    testdatapath = './data/tests/'

    # following are files used as input during the tests, don't remove these
    csvreadheaderfile = testdatapath + 'test_eight_specimen_records.csv'
    tsvreadheaderfile = testdatapath + 'test_three_specimen_records.txt'
    testcorrectioninputfile = testdatapath + 'test_specimen_correction.txt'
    testsetterinputfile = testdatapath + 'test_specimen_correction.txt'
    testmonthvocabfile = testdatapath + 'test_month.txt'

    # following are files output during the tests, remove these in dispose()
    testtokenreportfile = testdatapath + 'test_token_report_file.txt'
    testcorrectionreportfile = testdatapath + 'test_correction_report_file.txt'
    testsetterreportfile = testdatapath + 'test_setter_report_file.txt'

    def dispose(self):
        testtokenreportfile = self.testtokenreportfile
        testcorrectionreportfile = self.testcorrectionreportfile
        testsetterreportfile = self.testsetterreportfile
        if os.path.isfile(testtokenreportfile):
            os.remove(testtokenreportfile)
        if os.path.isfile(testcorrectionreportfile):
            os.remove(testcorrectionreportfile)
        if os.path.isfile(testsetterreportfile):
            os.remove(testsetterreportfile)
        return True

class ReportUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = ReportUtilsFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        csvreadheaderfile = self.framework.csvreadheaderfile
        tsvreadheaderfile = self.framework.tsvreadheaderfile
        testcorrectioninputfile = self.framework.testcorrectioninputfile

        s = csvreadheaderfile + ' does not exist'
        self.assertTrue(os.path.isfile(csvreadheaderfile), s)
        s = tsvreadheaderfile + ' does not exist'
        self.assertTrue(os.path.isfile(tsvreadheaderfile), s)
        s = testcorrectioninputfile + ' does not exist'
        self.assertTrue(os.path.isfile(testcorrectioninputfile), s)

    def test_term_setter_report(self):
        print 'testing term_setter_report'
        testsetterinputfile = self.framework.testsetterinputfile
        testsetterreportfile = self.framework.testsetterreportfile

        # Test field addition
        key = 'institutionCode'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='CAS')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country', 'institutionCode']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = tsv_dialect()
        with open(testsetterreportfile, 'rU') as outfile:
            dr = csv.DictReader(outfile, dialect=dialect, fieldnames=outputheader)
            # Read the header
            dr.next()
            # Read the first row of data
            firstrow = dr.next()

        field = 'institutionCode'
        value = firstrow[field]
        expected = 'CAS'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        # Test field list addition
        key = 'institutionCode|license'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='CAS|CC0')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country', 'institutionCode', 'license']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = tsv_dialect()
        with open(testsetterreportfile, 'rU') as outfile:
            dr = csv.DictReader(outfile, dialect=dialect, fieldnames=outputheader)
            # Read the header
            dr.next()
            # Read the first row of data
            firstrow = dr.next()

        field = 'institutionCode'
        value = firstrow[field]
        expected = 'CAS'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        field = 'license'
        value = firstrow[field]
        expected = 'CC0'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        # Test field replacement
        key = 'country'
        result = term_setter_report(testsetterinputfile, testsetterreportfile, 
            key, constantvalues='Argentina')
        s = 'term_setter_report() result not True '
        s += 'with inputfile: %s ' % testsetterinputfile
        s += 'and outputfile: %s' % testsetterreportfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testsetterreportfile)
        expected = ['ID', 'month', 'country']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = tsv_dialect()
        with open(testsetterreportfile, 'rU') as outfile:
            dr = csv.DictReader(outfile, dialect=dialect, fieldnames=outputheader)
            # Read the header
            dr.next()
            # Read the first row of data
            firstrow = dr.next()

        field = 'country'
        value = firstrow[field]
        expected = 'Argentina'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

    def test_term_standardizer_report(self):
        print 'testing term_standardizer_report'
        testcorrectioninputfile = self.framework.testcorrectioninputfile
        testcorrectionreportfile = self.framework.testcorrectionreportfile
        testmonthvocabfile = self.framework.testmonthvocabfile
    
        key = 'month'
        result = term_standardizer_report(testcorrectioninputfile, \
            testcorrectionreportfile, testmonthvocabfile, key)
        s = 'term_standardizer_report() result not True '
        s += 'with inputfile: %s ' % testcorrectioninputfile
        s += 'outpufile: %s' % testcorrectionreportfile
        s += 'and vocabfile: %s' % testmonthvocabfile
        self.assertTrue(result, s)
        
        outputheader = read_header(testcorrectionreportfile)
        expected = ['ID', 'month', 'country', 'month_orig']
        s = 'outputheader: %s not as expected: %s' % (outputheader, expected)
        self.assertEqual(outputheader, expected, s)

        dialect = tsv_dialect()
        with open(testcorrectionreportfile, 'rU') as outfile:
            dr = csv.DictReader(outfile, dialect=dialect, fieldnames=outputheader)
            # Read the header
            dr.next()
            # Read the first row of data
            firstrow = dr.next()

        field = 'month_orig'
        value = firstrow[field]
        expected = 'vi'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

        field = 'month'
        value = firstrow[field]
        expected = '6'
        s = 'Field %s value %s not as expected (%s)' % (field, value, expected)
        self.assertEqual(value, expected, s)

if __name__ == '__main__':
    print '=== report_utils.py ==='
    unittest.main()
