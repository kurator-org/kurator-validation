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
__version__ = "vocab_extractor.py 2016-08-31T21:57+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_vocab_utils import distinct_term_values_from_file
import os
import logging
import argparse

def vocab_extractor(options):
    """Extract a list of the distinct values of a set of terms in a text file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        inputfile - full path to the input file (required)
        workspace - path to a directory to work in (optional)
        terms - string of separator-separated terms for which to find distinct values
            (e.g., 'year', 'country|stateProvince|county') (required)
        separator - string that separates the values in terms (e.g., '|') 
            (optional; default None)
    returns a dictionary with information about the results
        workspace - path to a directory worked in
        extractedvalues - a list of distinct values of the term in the inputfile
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    setup_actor_logging(options)

    print '%s options: %s' % (__version__, options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'extractedvalues', 'success', 'message']

    # outputs
    workspace = None
    extractedvalues = None
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
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        terms = options['terms']
    except:
        terms = None

    if terms is None or len(terms)==0:
        message = 'No terms given'
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        separator = options['separator']
    except:
        separator = None

    extractedvalues = distinct_term_values_from_file(inputfile, terms, \
        separator=separator)
    print 'extractedvalues: %s' % extractedvalues
    success = True
    returnvals = [workspace, extractedvalues, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = "terms (required)"
    parser.add_argument("-t", "--terms", help=help)

    help = "separator (optional)"
    parser.add_argument("-s", "--separator", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.terms is None or len(options.terms)==0:
        s =  'syntax examples:\n'
        s += 'python vocab_extractor.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -w ./workspace'
        s += ' -t year'
        s += ' -s |'
        s += ' -l DEBUG\n'
        print '%s' % s
        s += 'python vocab_extractor.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -w ./workspace'
        s += '"country|stateprovince|county"'
        s += ' -s "|"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['workspace'] = options.workspace
    optdict['terms'] = options.terms
    optdict['separator'] = options.separator
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of terms from inputfile
    response=vocab_extractor(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
