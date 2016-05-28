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
__version__ = "text_file_aggregator.py 2016-05-27T21:19-03:00"

from dwca_utils import composite_header
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import glob
import csv
import uuid
import logging
import argparse

def text_file_aggregator(options):
    """Join the contents of files in a given path. Headers are not assumed to be the
       same. Write a file containing the joined files with one header line.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        inputpath - full path to the input file set (required)
        outputfile - name of the output file, without path (optional)
        workspace - path to a directory for the outputfile (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        aggregaterowcount - the number of rows in the aggregated file, not counting header
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'aggregaterowcount', 'success', 'message', 
        'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    success = False
    aggregaterowcount = None
    aggregateheader = None
    message = None
    dialect = None
    extension = ''

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None or len(outputfile)==0:
        outputfile='aggregate_'+str(uuid.uuid1())+extension

    # Construct the output file path in the workspace
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    try:
        inputpath = options['inputpath']
    except:
        inputpath = None

    if inputpath is None or len(inputpath)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, aggregaterowcount, success, message,
            artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        inputdialect = options['inputdialect']
    except:
        inputdialect = None

    if inputdialect == 'tsv':
        dialect = tsv_dialect()
        extension = '.tsv'
    elif inputdialect == 'excel' or inputdialect == 'csv.excel': 
        dialect = csv.excel
        extension = '.csv'

    aggregateheader = composite_header(inputpath, dialect)
    aggregaterowcount = 0

    # Open a file to write the aggregated results
    with open(outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=tsv_dialect(), 
            fieldnames=aggregateheader, extrasaction='ignore')
        writer.writeheader()
        files = glob.glob(inputpath)
        for file in files:
            if inputdialect is None:
                dialect = csv_file_dialect(file)
            with open(file, 'rU') as inputfile:
                reader = csv.DictReader(inputfile, dialect=dialect)
                for line in reader:
                    try:
                        writer.writerow(line)
                        aggregaterowcount += 1
                    except:
                        message = 'failed to write line:\n%s\nto file %s' % (line, file)
                        returnvals = [workspace, outputfile, aggregaterowcount, success, 
                            message, artifacts]
                        logging.debug('message:\n%s' % message)
                        return response(returnvars, returnvals)

    success = True
    artifacts['aggregated_file'] = outputfile
    if aggregateheader is not None:
        aggregateheader = list(aggregateheader)
        returnvals = [workspace, outputfile, aggregaterowcount, success, message,
            artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input files directory (required)'
    parser.add_argument("-i", "--inputpath", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputpath is None or len(options.inputpath)==0:
        s =  'syntax:\n'
        S += 'python text_file_aggregator.py'
        s += ' -i "./data/tests/test_tsv_*.txt"'
        s += ' -w ./workspace'
        s += ' -o aggregatedoutputfile.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputpath'] = options.inputpath
    optdict['outputfile'] = options.outputfile
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Aggregate files
    response=text_file_aggregator(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
