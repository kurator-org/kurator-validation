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
__version__ = "vocab_composite_extractor.py 2016-05-27T21:29-03:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_vocab_utils import distinct_composite_term_values_from_file
import os
import csv
import logging
import argparse

def vocab_composite_extractor(options):
    """Extract a list of the distinct values of a given keyfieldlist in a text file.    
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        inputfile - full path to the input file (required)
        keyfieldlist - order-dependent list of terms for which to 
            extract values. (required)
            Example for a geography key: 
            "continent|country|countryCode|stateProvince|
             county|municipality|waterBody|islandGroup|island"
    returns a dictionary with information about the results
        valueset - a list of distinct values of the temcomposite in the file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['valueset', 'success', 'message']

    # outputs
    valueset = None
    success = False
    message = None

    # inputs
    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [valueset, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [valueset, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        keyfieldlist = options['keyfieldlist']
    except:
        keyfieldlist = None

    if keyfieldlist is None or len(keyfieldlist)==0:
        message = 'No composite term given'
        returnvals = [valueset, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [valueset, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    valueset = distinct_composite_term_values_from_file(inputfile, keyfieldlist,'|')
    success = True
    returnvals = [valueset, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'ordered list of field names that make up the key (required)'
    parser.add_argument("-k", "--keyfieldlist", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.keyfieldlist is None or len(options.keyfieldlist)==0:
        s =  'syntax:\n'
        s += 'python vocab_composite_extractor.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -k "continent|country|stateprovince|county|'
        s += 'municipality|island|islandgroup|waterbody"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['keyfieldlist'] = options.keyfieldlist
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of keyfieldlist from inputfile
    response=vocab_composite_extractor(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
