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
__version__ = "darwin_cloud_collector.py 2016-05-11T15:58-03:00"

from optparse import OptionParser
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_utils import response
import os
import logging

def darwin_cloud_collector(options):
    """Get field names from inputfile and put any that are not Simple Darwin Core into 
       outputfile.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (required)
    returns a dictionary with information about the results
        addedvalues - new values added to the output file
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
#    print 'Started %s' % __version__
#    print 'options: %s' % options

    # Set up logging
#     try:
#         loglevel = options['loglevel']
#     except:
#         loglevel = None
#     if loglevel is not None:
#         if loglevel.upper() == 'DEBUG':
#             logging.basicConfig(level=logging.DEBUG)
#         elif loglevel.upper() == 'INFO':        
#             logging.basicConfig(level=logging.INFO)
# 
#     logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['addedvalues', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    addedvalues = None
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
        returnvals = [addedvalues, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [addedvalues, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given'
        returnvals = [addedvalues, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    header = read_header(inputfile)
#    print 'header: %s\n' % header
    nondwc = terms_not_in_dwc(header)
#    print 'nondwc: %s\n' % nondwc

    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(outputfile, nondwc, dialect)
    success = True
    artifacts['darwin_cloud_collector_file'] = outputfile
    returnvals = [addedvalues, outputfile, success, message, artifacts]
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Text file to store field names",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file (optional)",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
        options.outputfile is None or len(options.outputfile)==0:
        s =  'syntax: python darwin_cloud_collector.py'
        s += ' -i ./data/tests/test_eight_specimen_records.csv'
        s += ' -o dwc_cloud.txt'
        s += ' -w ./workspace'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct new field names to Darwin Cloud vocab file
    response=darwin_cloud_collector(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
