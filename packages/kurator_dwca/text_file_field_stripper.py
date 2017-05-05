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
__version__ = "text_file_field_stripper.py 2017-04-27T16:37-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import clean_header
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import read_csv_row
from dwca_utils import csv_dialect
from dwca_utils import tsv_dialect
from dwca_utils import extract_fields_from_row
import os
import uuid
import logging
import argparse

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

def text_file_field_stripper(options):
    ''' Filter a text file into a new file based on matching a list of fields to keep.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - the directory in which the output will be written (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (required)
        separator - string that separates the values in termlist (e.g., '|') 
            (optional; default None)
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
        termlist - list of fields to extract from the input file (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    format = 'txt'
    termlist = None
    separator = None
    encoding = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termlist = options['termlist']
    except:
        pass

    if termlist is None or len(termlist)==0:
        message = 'No termlist given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        separator = options['separator']
    except:
        pass

    try:
        encoding = options['encoding']
    except:
        pass

    if separator is None or len(separator.strip())==0:
        theterms = [termlist]
    else:
        theterms = termlist.split(separator)

    # Determine the file dialect
    inputdialect = csv_file_dialect(inputfile)

    # Determine the file encoding
    if encoding is None:
        encoding = csv_file_encoding(inputfile)

    # If the termname is not in the header of the inputfile, nothing to do.
    header = read_header(inputfile, dialect=inputdialect, encoding=encoding)

    # Make a clean version of the input header
    cleaninputheader = clean_header(header)

    try:
        format = options['format']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Prepare the outputfile
    if format=='txt' or format is None:
        outputdialect = tsv_dialect()
    else:
        outputdialect = csv_dialect()

    if separator is None or len(separator.strip())==0:
        theterms = [termlist]
    else:
        theterms = termlist.split(separator)

    # Make a clean version of the output header
    cleanoutputheader = clean_header(theterms)

    # Create the outputfile and write the new header to it
    write_header(outputfile, cleanoutputheader, outputdialect)

    # Check to see that the file was created
    if os.path.isfile(outputfile) == False:
        message = 'Outputfile %s was not created. %s' % (outputfile, __version__)
        returnvals = [workspace, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    # Open the outputfile to start writing matching rows
    with open(outputfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outputdialect, encoding='utf-8', 
            fieldnames=cleanoutputheader)

        # Iterate through all rows in the input file
        for row in read_csv_row(inputfile, dialect=inputdialect, encoding=encoding, 
            header=True, fieldnames=cleaninputheader):
            newrow = extract_fields_from_row(row, cleanoutputheader)
            writer.writerow(newrow)

    success = True
    s = 'stripped_file'
    artifacts[s] = outputfile
    
    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = "termlist (required)"
    parser.add_argument("-t", "--termlist", help=help)

    help = "separator (optional)"
    parser.add_argument("-s", "--separator", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python text_file_field_stripper.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testfilterout.txt'
        s += ' -f txt'
        s += ' -t "institutionCode|collectionCode|catalogNumber|year|country|scientificName"'
        s += ' -s "|"'
        s += ' -e utf-8'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['format'] = options.format
    optdict['termlist'] = options.termlist
    optdict['separator'] = options.separator
    optdict['encoding'] = options.encoding
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Split text file into chucks
    response=text_file_field_stripper(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_field_stripper"""
    main()
