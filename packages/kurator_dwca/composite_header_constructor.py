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
__version__ = "composite_header_constructor.py 2016-10-21T12:45+02:00"

from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import merge_headers
from dwca_utils import tsv_dialect
from dwca_utils import csv_dialect
from dwca_utils import response
from dwca_utils import setup_actor_logging
import logging
import argparse

def composite_header_constructor(options):
    ''' Create a file with a header that contains the distinct union of column names from 
        two input files.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the output file (optional; default './')
        inputfile1 - full path to one of the input files (optional)
        inputfile2 - full path to the second input file (optional)
        outputfile - name of the output file, without path (required)
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
    returns a dictionary with information about the results
        compositeheader - header combining two inputs
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'compositeheader', 'outputfile', 'success', 'message', \
        'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile1 = None
    inputfile2 = None
    outputfile = None
    format = 'txt'
    compositeheader = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile1 = options['inputfile1']
    except:
        pass

    try:
        inputfile2 = options['inputfile2']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given. %s' % __version__
        returnvals = [workspace, compositeheader, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Read the headers of the two files and let read_header figure out the dialects and
    # encodings.
    header1 = read_header(inputfile1)
    header2 = read_header(inputfile2)

    compositeheader = merge_headers(header1, header2)

    if format=='txt' or format is None:
        dialect = tsv_dialect()
    else:
        dialect = csv_dialect()

    # Write the resulting header into outputfile
    success = write_header(outputfile, compositeheader, dialect)
    if success == False:
        message = 'Header was not written. %s' % __version__
        returnvals = [workspace, compositeheader, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    if compositeheader is not None:
        compositeheader = list(compositeheader)

    artifacts['composite_header_file'] = outputfile

    returnvals = [workspace, compositeheader, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)
 
def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'full path to first input file'
    parser.add_argument("-1", "--file1", help=help)

    help = 'full path to second input file'
    parser.add_argument("-2", "--file2", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.outputfile is None or len(options.outputfile)==0 or \
        ((options.file1 is None or len(options.file1)==0) and \
         (options.file2 is None or len(options.file2)==0)):
        s =  'syntax:\n'
        s += 'python composite_header_constructor.py'
        s += ' -1 ./data/tests/test_tsv_1.txt'
        s += ' -2 ./data/tests/test_tsv_2.txt'
        s += ' -w ./workspace'
        s += ' -o test_compositeheader.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile1'] = options.file1
    optdict['inputfile2'] = options.file2
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict
    
    # Compose distinct field header from headers of files in inputpath
    response=composite_header_constructor(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
