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
__version__ = "term_count_reporter.py 2016-05-05T19:27-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_vocab_utils import distinct_term_counts_from_file
from dwca_vocab_utils import term_count_report
import os.path
import logging
import uuid

def term_count_reporter(options):
    """Extract a list of the distinct values of a given term in a text file along with 
       the number of times each occurs.
    options - a dictionary of parameters
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        termname - the name of the term for which to find distinct values (required)
        loglevel - the level at which to log
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
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
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    outputfile = None
    success = False
    message = None

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None:
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
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None:
        outputfile = '%s_count_report_%s.txt' % (termname, str(uuid.uuid1()))
    
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    counts = distinct_term_counts_from_file(inputfile, termname)
#    print 'counts: %s' % counts
    success = term_count_report(outputfile, counts)
    if success==True:
        s = '%s_count_report_file' % termname
        artifacts[s] = outputfile
        returnvals = [workspace, outputfile, success, message, artifacts]
#    logging.debug('options:\n%s' % options)
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Output file name, no path (optional)",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which distinct values are sought",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(DEBUG, INFO)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax: python term_count_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermcountout.txt'
        s += ' -w ./workspace'
        s += ' -t year'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel

    # Get distinct values of termname from inputfile
    response=term_count_reporter(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
