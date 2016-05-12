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
__version__ = "actor_template.py 2016-05-11T15:51-03:00"

from optparse import OptionParser
from dwca_utils import response
import os
import logging
import uuid

def dostuffer(options):
    """Generic actor showing patterns for logging, input dictionary, and output dictionary
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
    """
#    print 'Started %s' % __version__
#    print 'options: %s' % options

    # Set up logging
    try:
        loglevel = options['loglevel']
    except:
        loglevel = None
    if loglevel is not None:
        if loglevel.upper() == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        elif loglevel.upper() == 'INFO':        
            logging.basicConfig(level=logging.INFO)

    logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    outputfile = None
    success = False
    message = None

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None or len(outputfile)==0:
        outputfile='dwca_'+str(uuid.uuid1())+'.zip'

    # Construct the output file path in the workspace
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Do the actual work now that the preparation is complete
    success = do_stuff(inputfile, outputfile)

    # Add artifacts to the output dictionary if all went well
    if success==True:
        artifacts['output_file'] = outputfile

    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def do_stuff(inputfile, outputfile):
    """Generic function with input and output.
    parameters:
        inputfile - the full path to the input file
        outputfile - the full path to the output file
    returns:
        success - True if the task is completed, otherwise False
    """
    # Check for required values
    if inputfile is None or len(inputfile)==0:
        return False

    if outputfile is None or len(outputfile)==0:
        return False

    # Success
    return True

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Output file name, no path (optional)",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file (optional)",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
        options.outputfile is None or len(options.outputfile)==0:
        s =  'syntax: python actor_template.py'
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
    print 'response: %s' % response

if __name__ == '__main__':
    main()
