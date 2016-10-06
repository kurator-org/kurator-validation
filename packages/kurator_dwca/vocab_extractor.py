#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__version__ = "vocab_extractor.py 2016-10-06T11:50+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import extract_values_from_file
from dwca_utils import ustripstr
import os
import logging
import argparse

def vocab_extractor(options):
    ''' Extract a list of the distinct values of a set of terms in a text file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory to work in (optional)
        inputfile - full path to the input file (required)
        termlist - list of fields to extract from the input file (required)
        separator - string that separates the values in termlist (e.g., '|') 
            (optional; default None)
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
    returns a dictionary with information about the results
        workspace - path to a directory worked in
        extractedvalues - a list of distinct values of the term in the inputfile
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    # print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list of keys in the response dictionary
    returnvars = ['workspace', 'extractedvalues', 'success', 'message']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    extractedvalues = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    termlist = None
    separator = None
    encoding = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        termlist = options['termlist']
    except:
        pass

    if termlist is None or len(termlist)==0:
        message = 'No termlist given. %s' % __version__
        returnvals = [workspace, extractedvalues, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        separator = options['separator']
    except:
        pass

    try:
        encoding = options['encoding']
    except:
        pass

    # Extract the distinct values from the inputfile, applying the function to strip
    # white space and make lower case.
    # Let extract_values_from_file figure out the dialect and encoding of inputfile.
    extractedvalues = extract_values_from_file(inputfile, termlist, separator=separator,
        encoding=encoding, function=ustripstr)

    success = True
    returnvals = [workspace, extractedvalues, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = "termlist (required)"
    parser.add_argument("-t", "--term list", help=help)

    help = "separator (optional)"
    parser.add_argument("-s", "--separator", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termlist is None or len(options.termlist)==0:
        s =  'Single term syntax:\n'
        s += 'python vocab_extractor.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t year'
        s += ' -e utf-8'
        s += ' -l DEBUG\n'
        print '%s' % s

        s =  'Multiple term syntax:\n'
        s += 'python vocab_extractor.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += '"country|stateprovince"'
        s += ' -s "|"'
        s += ' -e utf-8'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['termlist'] = options.termlist
    optdict['separator'] = options.separator
    optdict['encoding'] = options.encoding
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of a list of terms from inputfile
    response=vocab_extractor(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
