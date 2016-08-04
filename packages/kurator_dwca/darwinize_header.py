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
__version__ = "darwinize_header.py 2016-08-04T14:26+02:00"

from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_vocab_utils import darwinize_list
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import read_csv_row
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import logging
import argparse
import commands
import csv

def darwinize_header(options):
    """Translate field names from input file to Darwin Core field names in outputfile
       using a Darwin Cloud vocabulary lookup.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        dwccloudfile - full path to the vocabulary file containing the Darwin Cloud 
           terms (required)
        outputfile - name of the output file, without path (required)
    returns a dictionary with information about the results
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    success = False
    message = None

    # inputs
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

    try:
        dwccloudfile = options['dwccloudfile']
    except:
        dwccloudfile = None

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if dwccloudfile is None or len(dwccloudfile)==0:
        message = 'No Darwin Cloud vocabulary file given'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(dwccloudfile) == False:
        message = 'Darwin Cloud vocabulary file not found'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    dialect = csv_file_dialect(inputfile)
    encoding = csv_file_encoding(inputfile)
    header = read_header(inputfile)
    dwcheader = darwinize_list(header, dwccloudfile)

    # Write the new header to the outputfile
    if write_header(outputfile, dwcheader, dialect) == False:
        message = 'Unable to write header to output file'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Read the rows of the input file, append them to the output file after the 
    # header with columns in the same order.
    with open(outputfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=dialect, fieldnames=header)
        for row in read_csv_row(inputfile, dialect, encoding):
            writer.writerow(row)

    success = True
    artifacts['darwinized_header_file'] = outputfile
    returnvals = [outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the Darwin Cloud vocabulary file (required)'
    parser.add_argument("-v", "--dwccloudfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
        options.outputfile is None or len(options.outputfile)==0:
        s =  'syntax:\n'
        s += 'python darwinize_header.py'
        s += ' -i ./data/tests/test_eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/dwc_cloud.txt'
        s += ' -o darwinized.csv'
        s += ' -w ./workspace'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['workspace'] = options.workspace
    optdict['dwccloudfile'] = options.dwccloudfile
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct new field names to Darwin Cloud vocab file
    response=darwinize_header(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()