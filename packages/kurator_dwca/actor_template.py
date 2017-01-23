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
__version__ = "actor_template.py 2017-01-05T18:24-03:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import logging
import uuid
import argparse

def dostuffer(options):
    ''' Generic actor showing patterns for logging, input dictionary, and output dictionary
        with artifacts.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the results
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list of keys in the response dictionary
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    # Intialize any other output variables here so that the response calls no about them

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    inputfile = None
    outputfile = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        workspace = './'

    try:
        inputfile = options['inputfile']
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
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        outputfile='dwca_'+str(uuid.uuid1())+'.zip'

    # Construct the output file path in the workspace
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    ### Optional inputs ###

    # Do the actual work now that the preparation is complete
    success = do_stuff(inputfile, outputfile)

    # Add artifacts to the output dictionary if all went well
    if success==True:
        artifacts['template_output_file'] = outputfile

    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def do_stuff(inputfile, outputfile):
    ''' Generic function with input and output.
    parameters:
        inputfile - the full path to the input file
        outputfile - the full path to the output file
    returns:
        success - True if the task is completed, otherwise False
    '''
    functionname = 'do_stuff()'

    # Check for required values
    if inputfile is None or len(inputfile)==0:
        s = 'No input file given in %s.' % functionname
        logging.debug(s)
        return False

    if outputfile is None or len(outputfile)==0:
        s = 'No output file given in %s.' % functionname
        logging.debug(s)
        return False

    s = 'Stuff written to %s in %s.' % (outputfile, functionname)
    logging.debug(s)
    # Success
    return True

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

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

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python actor_template.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o test_ccber_mammals_dwc_archive.zip'
        s += ' -w ./workspace'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of to vocab file
    response=dostuffer(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
