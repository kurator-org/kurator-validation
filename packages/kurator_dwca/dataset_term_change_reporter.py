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
__version__ = "dataset_term_change_reporter.py 2016-09-25T18:25+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from report_utils import term_corrector_report
from slugify import slugify
import os.path
import logging
import argparse

def dataset_term_change_reporter(options):
    """Create a report for an input file with key field replaced by standard value and 
       added field for the original value.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the output file (optional)
        inputfile - path to the input file. Either full path or path within the workspace
            (required)
        outputfile - name of the output file, without path (optional)
        vocabfile - path to the vocabulary file. Either full path or path within the
           workspace (required if constantvalues is None)
        format - output file format (e.g., 'csv' or 'txt') (optional; default txt)
        key - field or separator-separated fields whose values are to be set to the 
            constantvalues (required)
        separator - string to use as the key and value separator (optional; default '|')
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    # print '%s options: %s' % (__version__, options)

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

    ### Required inputs ###
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
        message = 'No input file given in %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if the input file is at the absolute path or in the workspace.
    if os.path.isfile(inputfile) == False:
        if os.path.isfile(workspace+'/'+inputfile) == True:
            inputfile = workspace+'/'+inputfile
        else:
            message = 'Input file %s not found in %s' % (inputfile, __version__)
            returnvals = [workspace, outputfile, True, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given in %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if vocab file is at the absolute path or in the workspace.
    vocabfileat = None
    if os.path.isfile(vocabfile) == True:
        vocabfileat = vocabfile
    else:
        vocabfileat = workspace+'/'+vocabfile

    vocabfile = vocabfileat

    try:
        key = options['key']
    except:
        key = None

    if key is None or len(key)==0:
        message = 'No key given in %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    ### Optional inputs ###
    try:
        separator = options['separator']
    except:
        separator = None

    try:
        format = options['format']
    except:
        format = None

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None:
        outputfile = '%s/%s_changed_report_%s.%s' % \
          (workspace.rstrip('/'), slugify(key), str(uuid.uuid1()), format)
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get a list of distinct values of the term in the input file
    fields = key.split(separator)

    success = term_corrector_report(inputfile, outputfile, vocabfile, key, \
        separator=separator, format=format)

    if outputfile is not None and not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s' % outputfile
        message += 'in %s' %__version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = '%s_change_report_file' % slugify(key)
    artifacts[s] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'full path to the vocab file (required if constantvalues is None)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'field with the distinct values in the vocabulary file (required)'
    parser.add_argument("-k", "--key", help=help)

    help = 'string that separates fields in the key (optional)'
    parser.add_argument("-s", "--separator", help=help)

    help = 'report file format (e.g., csv or txt) (optional; default csv)'
    parser.add_argument("-f", "--format", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.key is None or len(options.key)==0 or \
       ((options.vocabfile is None or len(options.vocabfile)==0) and \
       options.constantvalues is None):
        s =  'Example syntax:\n'
        s += 'python dataset_term_change_reporter.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermchangeoutput.csv'
        s += ' -v ./data/vocabularies/country.txt'
        s += ' -k country'
        s += ' -f csv'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['key'] = options.key
    optdict['separator'] = options.separator
    optdict['format'] = options.format
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=dataset_term_change_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
