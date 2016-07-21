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
__version__ = "text_file_filter.py 2016-07-21T13:38+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import read_header
from dwca_utils import csv_file_dialect
from dwca_utils import csv_dialect
from dwca_utils import tsv_dialect
import os
import uuid
import logging
import argparse
import csv

def text_file_filter(options):
    """Filter a text file into a new file with header based on matching values in a term.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        inputfile - full path to the input file (required)
        workspace - the directory in which the output will be written (optional)
        outputfile - name of the output file, without path (optional)
        format - output file format (e.g., 'csv' or 'txt') (optional)
        termname - the name of the term for which to find distinct values (required)
        matchingvalue - the value to use as a filter for the term (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    outputfile = None
    format = None
    success = False
    message = None
    matchingvalue = None

    # inputs
    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        matchingvalue = options['matchingvalue']
    except:
        matchingvalue = None

    if matchingvalue is None or len(matchingvalue)==0:
        message = 'No matching value given for %s' % termname
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # If the termname is not in the header of the inputfile, nothing to do
    header = read_header(inputfile)
    if termname not in header:
        message = 'Term %s not found in %s' % (termname, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
#    print 'header: %s' % header
 
    try:
        format = options['format']
    except:
        format = None

    if format is None:
        format = 'csv'

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        outputfile = '%s_count_report_%s.%s' % (termname, str(uuid.uuid1()), format)
    
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Determine the file dialect
    indialect = csv_file_dialect(inputfile)
    
    # Prepare the outputfile
    if format=='csv' or format is None:
        outdialect = csv_dialect()
    else:
        outdialect = tsv_dialect()

    # Create the outputfile with the chsen format and the same header as the input
    with open(outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=outdialect, fieldnames=header)
        writer.writeheader()

    # Check to see that the file was created
    if os.path.isfile(outputfile) == False:
        message = 'Outputfile %s was not created' % outputfile
        returnvals = [workspace, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    # Open the outputfile to start writing matching rows
    with open(outputfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=outdialect, fieldnames=header)
        with open(inputfile, 'rU') as infile:
            dr = csv.DictReader(infile, dialect=indialect, fieldnames=header)
            # Iterate though the entire input file
            for row in dr:
                # Determine if the term value matches the criterion
#                print 'row: %s' % row
                if row[termname] == matchingvalue:
                    writer.writerow(row)

    success = True
    s = '%s_filtered_file' % termname
    artifacts[s] = outputfile
    
    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = "value to match (required)"
    parser.add_argument("-m", "--matchingvalue", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python text_file_filter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testfilterout.txt'
        s += ' -w ./workspace'
        s += ' -t year'
        s += ' -f txt'
        s += ' -m 1990'
        s += ' -l DEBUG'
        print '%s' % s
        return

    try:
        chunksize = int(str(options.chunksize))
    except:
        chunksize = 10000

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['workspace'] = options.workspace
    optdict['format'] = options.format
    optdict['matchingvalue'] = options.matchingvalue
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Split text file into chucks
    response=text_file_filter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_filter"""
    main()
