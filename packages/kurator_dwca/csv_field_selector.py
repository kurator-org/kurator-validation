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
__copyright__ = "Copyright 2018 President and Fellows of Harvard College"
__version__ = "csv_field_selector.py 2018-01-30T14:35-05:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import csv_select_fields
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import logging
import argparse

def csv_field_selector(options):
    ''' Create a new file by selecting only fields in a termlist in the order given in
        that list.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory to work in (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (required)
        termlist - list of fields to extract from the input file (required)
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
    returns a dictionary with information about the results
        outputfile - actual full path to the output file
        workspace - path to a directory for the output artifacts
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Custom outputs ###

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    termlist = None
    encoding = None
    format = 'txt'

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
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
        format = options['format']
    except:
        pass

    try:
        encoding = options['encoding']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Do the field selection. Let the selector figure out the input dialect.
    success = csv_select_fields(inputfile, outputfile, termlist, dialect=None, 
        encoding=encoding, format=format)

    if success == False:
        message = 'Unable to select fields from %s. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)
        
    artifacts['selected_field_file'] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = "termlist (required)"
    parser.add_argument("-t", "--termlist", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'output file format (e.g., csv or txt) (optional; default txt)'
    parser.add_argument("-f", "--format", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python csv_field_selector.py'
        s += ' -w ./workspace'
        s += ' -i ./data/tests/test_eight_specimen_records'
        s += ' -o fieldsselected.csv'
        s += ' -t country|stateprovince|county'
        s += ' -e utf8'
        s += ' -f txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termlist'] = options.termlist
    optdict['encoding'] = options.encoding
    optdict['format'] = options.format
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Check if any rows do not have fields matching header field count
    response=csv_field_selector(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
