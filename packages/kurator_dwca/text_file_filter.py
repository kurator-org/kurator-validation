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
__version__ = "text_file_filter.py 2016-09-29T13:05+02:00"

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
try:
    # need to install unicodecsv for this to be used
    # pip install unicodecsv
    # jython pip install unicodecsv for use in workflows
    import unicodecsv as csv
except ImportError:
    import warnings
    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv

def text_file_filter(options):
    """Filter a text file into a new file based on matching values in a term.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - the directory in which the output will be written (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
        termname - the name of the term for which to find distinct values (required)
        matchingvalue - the value to use as a filter for the term (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    # print '%s options: %s' % (__version__, options)

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
    termname = None
    matchingvalue = None

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
        message = 'No input file given'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found' % inputfile
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        pass

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        matchingvalue = options['matchingvalue']
    except:
        pass

    if matchingvalue is None or len(matchingvalue)==0:
        message = 'No matching value given for %s' % termname
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    # If the termname is not in the header of the inputfile, nothing to do
    header = read_header(inputfile)
    if termname not in header:
        message = 'Term %s not found in %s' % (termname, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
 
    try:
        format = options['format']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        outputfile = '%s_count_report_%s.%s' % (termname, str(uuid.uuid1()), format)
    
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Determine the file dialect
    indialect = csv_file_dialect(inputfile)
    
    # Prepare the outputfile
    if format=='txt' or format is None:
        outdialect = tsv_dialect()
    else:
        outdialect = csv_dialect()

    # Create the outputfile with the chosen format and the same header as the input
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

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = "value to match (required)"
    parser.add_argument("-m", "--matchingvalue", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python text_file_filter.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testfilterout.txt'
        s += ' -f txt'
        s += ' -t year'
        s += ' -m 1990'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['format'] = options.format
    optdict['termname'] = options.termname
    optdict['matchingvalue'] = options.matchingvalue
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Split text file into chucks
    response=text_file_filter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_filter"""
    main()
