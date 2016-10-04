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
__version__ = "text_file_aggregator.py 2016-10-04T13:24+02:00"

from dwca_utils import composite_header
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import utf8_data_encoder
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import glob
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
    s += "jython pip install unicodecsv"
    warnings.warn(s)

def text_file_aggregator(options):
    ''' Join the contents of files in a given path. Headers are not assumed to be the
        same. Write a file containing the joined files with one header line.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputpath - full path to the input file set. The file extension of the outputfile
            will be the substring following the last '.' in the inputpath.
            Example: ./workspace/thefiles.txt will produce an output file ending in
            '.txt' (required) 
        outputfile - name of the output file, without path (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        aggregaterowcount - the number of rows in the aggregated file, not counting header
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    # print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'aggregaterowcount', 'success', 'message', 
        'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    aggregaterowcount = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputpath = None
    outputfile = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputpath = options['inputpath']
    except:
        pass

    if inputpath is None or len(inputpath)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, aggregaterowcount, success, message,
            artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        # Get the extension as the substring of the inputpath following the last '.'
        extension = inputpath.split('.')[-1]
        outputfile='aggregate_'+str(uuid.uuid1())+extension

    # Construct the output file path in the workspace
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    aggregateheader = composite_header(inputpath, dialect=None)
    aggregaterowcount = 0

    # Open a file to write the aggregated results
    with open(outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=tsv_dialect(), 
            fieldnames=aggregateheader, extrasaction='ignore')
        writer.writeheader()
        files = glob.glob(inputpath)
        for file in files:
            dialect = csv_file_dialect(file)
            encoding = csv_file_encoding(file)
            with open(file, 'rU') as inputfile:
                reader = csv.DictReader(utf8_data_encoder(inputfile, encoding), 
                    dialect=dialect, encoding=encoding)
                for line in reader:
                    try:
                        writer.writerow(line)
                        aggregaterowcount += 1
                    except:
                        message = 'failed to write line:\n%s\n' % line
                        message += 'to file %s. %s' % (file, __version__)
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
    '''Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input files directory (required)'
    parser.add_argument("-i", "--inputpath", help=help)

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

    optdict['workspace'] = options.workspace
    optdict['inputpath'] = options.inputpath
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Aggregate files
    response=text_file_aggregator(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
