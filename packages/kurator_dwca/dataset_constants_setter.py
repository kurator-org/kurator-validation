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
__version__ = "dataset_constants_setter.py 2017-04-27T16:37-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from report_utils import term_setter_report
from slugify import slugify
import os.path
import logging
import argparse

def dataset_constants_setter(options):
    ''' Create an output file replacing values in fields of an input file with constants 
        and adding fields that did not already exist in the input file, filling them with 
        constants.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the output file (optional; default './')
        inputfile - path to the input file. Either full path or path within the workspace
            (required)
        outputfile - name of the output file, without path (optional)
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
        key - field or separator-separated fields whose values are to be set to the 
            constantvalues (required)
        separator - string to use as the key and value separator (optional; default '|')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
        constantvalues - value or separator-separated vslues to set the field(s) to
            (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list of keys in the response dictionary
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    format = 'txt'
    key = None
    separator = '|'
    constantvalues = None
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
            returnvals = [workspace, outputfile, True, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        key = options['key']
    except:
        pass

    if key is None or len(key)==0:
        message = 'No key given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    ### Optional inputs ###
    try:
        format = options['format']
    except:
        pass

    try:
        separator = options['separator']
    except:
        pass

    try:
        encoding = options['encoding']
    except:
        pass

    try:
        constantvalues = options['constantvalues']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile.strip())==0:
        outputfile = '%s/%s_corrected_report_%s.%s' % \
          (workspace.rstrip('/'), slugify(key), str(uuid.uuid1()), format)
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get a list of distinct values of the term in the input file
    fields = key.split(separator)

    # Run the core operation
    success = term_setter_report(inputfile, outputfile, key, \
        constantvalues=constantvalues, separator=separator, encoding=encoding, 
        format=format)

    # Check to see if the outputfile was created
    if outputfile is not None and not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s. ' % outputfile
        message += '%s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Add artifacts to the output dictionary if all went well
    s = '%s_setter_report_file' % slugify(key)
    artifacts[s] = outputfile

    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    '''Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'field with the distinct values in the vocabulary file (required)'
    parser.add_argument("-k", "--key", help=help)

    help = 'constant to set the key to for all records (optional)'
    parser.add_argument("-c", "--constantvalues", help=help)

    help = 'string that separates fields in the key (optional)'
    parser.add_argument("-s", "--separator", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

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
       options.constantvalues is None or len(options.constantvalues)==0:
        s =  'Example syntax:\n'
        s += 'python dataset_constants_setter.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testdatasetconstantsout.txt'
        s += ' -k "license|modified"'
        s += ' -c "CC0|2016-09-25"'
        s += ' -s "|"'
        s += ' -e utf-8'
        s += ' -f txt'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['key'] = options.key
    optdict['constantvalues'] = options.constantvalues
    optdict['separator'] = options.separator
    optdict['encoding'] = options.encoding
    optdict['format'] = options.format
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=dataset_constants_setter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
