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
__version__ = "term_counter.py 2016-10-21T12:47+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import term_rowcount_from_file
import os
import logging
import argparse

def term_counter(options):
    ''' Get a count of the rows that are populated for a given term.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the output artifacts (optional)
        inputfile - full path to the input file (required)
        termname - the name of the term for which to count rows (required)
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
    returns a dictionary with information about the results
        workspace - path to a directory for the output artifacts
        rowcount - the number of rows in the inputfile that have a value for the term
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'rowcount', 'success', 'message']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    rowcount = None

    ### Establish variables ###
    workspace = './'
    inputfile = None
    termname = None
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
        returnvals = [workspace, rowcount, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, rowcount, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        pass

    if termname is None or len(termname)==0:
        message = 'No term given. %s' % __version__
        returnvals = [workspace, rowcount, success, message]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        encoding = options['encoding']
    except:
        pass

    rowcount = term_rowcount_from_file(inputfile, termname, encoding=encoding)

    success = True
    returnvals = [workspace, rowcount, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax:\n'
        s += 'python term_counter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -t year'
        s += ' -e utf-8'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['termname'] = options.termname
    optdict['encoding'] = options.encoding
    print 'optdict: %s' % optdict

    # Get distinct values of termname from inputfile
    response=term_counter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
