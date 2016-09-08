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
__version__ = "utf8_encoder.py 2016-09-08T14:06+02:00"

from dwca_utils import ENCODINGS
from dwca_utils import utf8_file_encoder
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import logging
import argparse

def utf8_encoder(options):
    """Translate input file from its current encoding to utf8.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (required)
        encoding - the encoding of the input file (optional)
    returns a dictionary with information about the results
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # print '%s options: %s' % (__version__, options)

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
        outputfile = options['outputfile']
    except:
        outputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found' % inputfile
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given'
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    try:
        encoding = options['encoding']
    except:
        encoding = None

    success = utf8_file_encoder(inputfile, outputfile, encoding)

    if success == False:
        message = 'Unable to translate %s to utf8 encoding' % inputfile
        returnvals = [outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)
        
    artifacts['utf8_encoded_file'] = outputfile
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

    help = 'current encoding (optional)'
    parser.add_argument("-e", "--encoding", help=help)

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
        s += 'python utf8_encoder.py'
        s += ' -i ./data/tests/test_thirty_records_mac_roman_crlf.csv'
        s += ' -o as_utf8.csv'
        s += ' -w ./workspace'
        s += ' -e mac_roman'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['encoding'] = options.encoding
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct new field names to Darwin Cloud vocab file
    response=utf8_encoder(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
