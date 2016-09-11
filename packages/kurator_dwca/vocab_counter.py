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
__version__ = "vocab_counter.py 2016-09-11T17:18+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import extract_value_counts_from_file
import os.path
import logging
import argparse

def vocab_counter(options):
    """Extract a list of the distinct values of a given term in a text file along with 
       the number of times each occurs.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        inputfile - full path to the input file (required)
        termname - the name of the term for which to find distinct values (required)
    returns a dictionary with information about the results
        extractedvalues - a list of distinct values of the term in the inputfile, with a
           count of the number of times it occurs
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

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
    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    extractedvalues = extract_value_counts_from_file(inputfile, [termname])
    success = True
    returnvals = [extractedvalues, success, message]
    options['vocab_counter_response'] = response(returnvars, returnvals)
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax:\n'
        s += 'python vocab_counter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t year'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['termname'] = options.termname
    optdict['loglevel'] = options.loglevel

    # Get distinct values of termname from inputfile
    response=vocab_counter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
