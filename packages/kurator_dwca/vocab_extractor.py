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
__version__ = "vocab_extractor.py 2016-04-08T13:03-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_vocab_utils import distinct_term_values_from_file
import os.path
import logging

# Example: 
#
# kurator -f vocab_extractor.yaml 
#         -p i=../data/eight_specimen_records.csv 
#         -p t=year
#
# or as a command-line script.
# Example:
#
# python vocab_extractor.py 
#        -i ./data/eight_specimen_records.csv 
#        -t year

def vocab_extractor(options):
    """Extract a list of the distinct values of a given term in a text file.
    options - a dictionary of parameters
        inputfile - full path to the input file
        termname - the name of the term for which to find distinct values
        loglevel - the level at which to log
    returns a dictionary with information about the results
        extractedvalues - a list of distinct values of the term in the inputfile
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Set up logging
    try:
        loglevel = options['loglevel']
    except:
        loglevel = None
    if loglevel is not None:
        if loglevel.upper() == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        elif loglevel.upper() == 'INFO':        
            logging.basicConfig(level=logging.INFO)

    logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['extractedvalues', 'success', 'message']

    # outputs
    extractedvalues = None
    success = False
    message = None

    # inputs
    try:
        inputfile = options['inputfile']
    except:
        inputfile = None
    try:
        termname = options['termname']
    except:
        termname = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    extractedvalues = distinct_term_values_from_file(inputfile, termname)
    success = True
    returnvals = [extractedvalues, success, message]
    options['vocab_extractor_response'] = response(returnvars, returnvals)
    logging.debug('options:\n%s' % options)
    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which distinct values are sought",
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
        s =  'syntax: python vocab_extractor.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t year'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['termname'] = options.termname
    optdict['loglevel'] = options.loglevel

    # Get distinct values of termname from inputfile
    response=vocab_extractor(optdict)
#    print 'response: %s' % response

if __name__ == '__main__':
    main()
