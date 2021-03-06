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
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "darwin_cloud_collector.py 2017-04-27T16:37-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import logging
import argparse

def darwin_cloud_collector(options):
    ''' Get field names from inputfile and put any that are not Simple Darwin Core into 
       outputfile.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (required)
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
    returns a dictionary with information about the results
        addedvalues - new values added to the output file
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'addedvalues', 'outputfile', 'success', 'message', \
        'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    addedvalues = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
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

    try:
        outputfile = options['outputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, addedvalues, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, addedvalues, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given. %s' % __version__
        returnvals = [workspace, addedvalues, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    try:
        encoding = options['encoding']
    except:
        pass

   # Read the header and let read_header figure out the dialect and encoding.
    header = read_header(inputfile, encoding=encoding)
    nondwc = terms_not_in_dwc(header, casesensitive=False)

    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(outputfile, nondwc, 'fieldname', 
        dialect=dialect)
    success = True

    if addedvalues is not None:
        artifacts['darwin_cloud_collector_file'] = outputfile

    returnvals = [workspace, addedvalues, outputfile, success, message, artifacts]
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

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
        options.outputfile is None or len(options.outputfile)==0:
        s =  'syntax:\n'
        s += 'python darwin_cloud_collector.py'
        s += ' -w ./workspace'
        s += ' -i ./data/tests/test_eight_specimen_records.csv'
        s += ' -o dwc_cloud.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct new field names to Darwin Cloud vocab file
    response=darwin_cloud_collector(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
