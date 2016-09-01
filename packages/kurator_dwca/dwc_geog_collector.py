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
__version__ = "dwc_geog_collector.py 2016-08-27T21:39+02:00"

from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import not_in_list
from dwca_vocab_utils import geogvocabheader
from dwca_utils import read_header
from dwca_terms import geogkeytermlist
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import csv
import logging
import argparse

def dwc_geog_collector(options):
    """Get geography unique combinations of geography from the inputfile and put any new 
        ones in the geography vocabulary file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory to work in (optional)
        inputfile - path to the input file. Either full path or path within the workspace
            (required)
        vocabfile - path to the geography vocabulary file. Either full path or path 
           within the workspace (required)
    returns a dictionary with information about the results
        workspace - path to a directory worked in
        addedvalues - new values added to the geography vocabulary file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    setup_actor_logging(options)

    print '%s options: %s' % (__version__, options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'addedvalues', 'success', 'message']

    # outputs
    workspace = None
    addedvalues = None
    success = False
    message = None

    # inputs
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
        message = 'No input file given'
        returnvals = [workspace, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given'
        returnvals = [workspace, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if vocab file is at the absolute path or in the workspace.
    vocabfileat = None
    if os.path.isfile(vocabfile) == True:
        vocabfileat = vocabfile
    elif os.path.isfile(workspace+'/'+vocabfile) == True:
        vocabfileat = workspace+'/'+vocabfile
    else:
        message = 'Vocab file not found'
        returnvals = [workspace, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    dialect = vocab_dialect()

    geogkey = compose_key_from_list(geogkeytermlist)

    potentialgeogs = distinct_term_values_from_file(inputfile, geogkey, separator='|')
    logging.debug('potentialgeogs: %s\n' % potentialgeogs)

    existinggeogs = distinct_term_values_from_file(vocabfile, geogkey, dialect=dialect)
    logging.debug('existinggeogs: %s\n' % existinggeogs)

    addedvalues = not_in_list(existinggeogs, potentialgeogs)
    logging.debug('added geog values: %s\n' % addedvalues)

    # Now write the newgeogs to the geog vocab file, which has a distinct header
    # If the geog vocab file does not exist, make it
    geogheader = geogvocabheader()
    logging.debug('geog header: %s\n' % geogheader)

    if not os.path.isfile(vocabfile):
        writevocabheader(vocabfile, geogheader, dialect)

    # Should have a vocab file now
    # If the geog vocab file header does not match
    checkheader = read_header(vocabfile, dialect)
    if checkheader != geogheader:
        message = 'header read from ' + vocabfile + 'does not match geogvocabheader'
        returnvals = [workspace, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Add the new geogs to the geog vocab file
    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=geogheader)
        for term in addedvalues:
            writer.writerow({'geogkey':term, 'vetted':0, 'unresolved':0 })
    success = True

    returnvals = [workspace, addedvalues, success, message]
    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'full path to the vocab file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
        options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax:\n'
        s += 'python dwc_geog_collector.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/dwc_geography.txt'
        s += ' -w ./workspace'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of to vocab file
    response=dwc_geog_collector(optdict)
    print '\nresponse: %s' % response
#    logging.debug('To file %s, added new values: %s' % (inputfile, response['addedvalues']))

if __name__ == '__main__':
    main()
