#!/usr/bin/env python
# -*- coding: utf8 -*-

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
__version__ = "term_completeness_reporter.py 2016-10-20T16:45+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import write_header
from dwca_utils import csv_dialect
from dwca_utils import tsv_dialect
from dwca_utils import split_path
from dwca_utils import term_completeness_from_file
from report_utils import term_completeness_report
import logging
import os
import uuid
import argparse

# Replace the system csv with unicodecsv. All invocations of csv will use unicodecsv,
# which supports reading and writing unicode streams.
try:
    import unicodecsv as csv
except ImportError:
    import warnings
    s = "The unicodecsv package is required.\n"
    s += "pip install unicodecsv\n"
    s += "$JYTHON_HOME/bin/pip install unicodecsv"
    warnings.warn(s)

def term_completeness_reporter(options):
    ''' Extract a list of the fields in a text file along with the number of rows in which
        the field is populated.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'csv')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    #logging.debug( 'Started %s' % __version__ )
    #logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None
    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    format = None
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
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if the input file is at the absolute path or in the workspace.
    if os.path.isfile(inputfile) == False:
        if os.path.isfile(workspace+'/'+inputfile) == True:
            inputfile = workspace+'/'+inputfile
        else:
            message = 'Input file %s not found. %s' % (inputfile, __version__)
            returnvals = [workspace, outputfile, success, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        format = options['format']
    except:
        pass

    if format is None:
        format = 'csv'

    try:
        encoding = options['encoding']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile.strip())==0:
        path, ext, filename = split_path(inputfile)
        outputfile = '%s/%s_term_completeness_report.%s' % \
          (workspace.rstrip('/'), filename, format)
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get the list of values for the field given by termname along with their counts.
    fieldcountdict = term_completeness_from_file(inputfile, encoding=encoding)
    # print 'counts: %s' % counts

    #Try to create the report for the term value counts.
    success = term_completeness_report(outputfile, fieldcountdict, format=format)

    if success==False:
        message = 'No count report created for %s from %s. ' % (termname, outputfile)
        message += '%s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
    
    s = 'field_completeness_report_file'
    artifacts[s] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.outputfile is None or len(options.outputfile)==0:
        s =  'Single field syntax:\n'
        s += 'python term_completeness_reporter.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermcompletenessout.txt'
        s += ' -f csv'
        s += ' -e utf-8'
        print '%s' % s

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['format'] = options.format
    optdict['encoding'] = options.encoding
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of termname from inputfile
    response=term_completeness_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
