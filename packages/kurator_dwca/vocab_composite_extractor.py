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
__version__ = "vocab_composite_extractor.py 2016-05-11T21:37-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_vocab_utils import distinct_composite_term_values_from_file
import os
import csv
import logging

def vocab_composite_extractor(options):
    """Extract a list of the distinct values of a given termcomposite in a text file.    
    options - a dictionary of parameters
        loglevel - the level at which to log (optional)
        inputfile - full path to the input file (required)
        termcomposite - order-dependent list of terms for which to 
            extract values. (required)
            Example for a geography key: 
            "continent|country|countryCode|stateProvince|
             county|municipality|waterBody|islandGroup|island"
    returns a dictionary with information about the results
        valueset - a list of distinct values of the temcomposite in the file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
#     print 'Started %s' % __version__
#     print 'options: %s' % options

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
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [valueset, success, message]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        termcomposite = options['termcomposite']
    except:
        termcomposite = None

    if termcomposite is None or len(termcomposite)==0:
        message = 'No composite term given'
        returnvals = [valueset, success, message]
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [valueset, success, message]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    valueset = distinct_composite_term_values_from_file(inputfile, termcomposite,'|')
    success = True
    returnvals = [valueset, success, message]
#    logging.debug('options:\n%s' % options)
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-t", "--termcomposite", dest="termcomposite",
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
       options.termcomposite is None or len(options.termcomposite)==0:
        s =  'syntax: python vocab_composite_extractor.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t "continent|country|stateprovince|county|'
        s += 'municipality|island|islandgroup|waterbody"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['termcomposite'] = options.termcomposite
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of termcomposite from inputfile
    response=vocab_composite_extractor(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
