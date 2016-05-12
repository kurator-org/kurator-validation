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
__version__ = "term_counter.py 2016-05-11T16:06-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_utils import term_rowcount_from_file
import os
import logging

def term_counter(options):
    """Get a count of the rows that are populated for a given term.
    options - a dictionary of parameters
        inputfile - full path to the input file (required)
        termname - the name of the term for which to count rows (required)
    returns a dictionary with information about the results
        rowcount - the number of rows in the inputfile that have a value for the term
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
    returnvars = ['rowcount', 'success', 'message']

    # outputs
    rowcount = None
    success = False
    message = None

    # inputs
    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [rowcount, success, message]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    rowcount = term_rowcount_from_file(inputfile, termname)
    success = True
    returnvals = [rowcount, success, message]
#    logging.debug('message:\n%s' % message)
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which distinct values are sought",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax: python term_counter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t year'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['termname'] = options.termname
    print 'optdict: %s' % optdict

    # Get distinct values of termname from inputfile
    response=term_counter(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
