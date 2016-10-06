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
__version__ = "vocab_appender.py 2016-10-06T13:45+02:00"

from dwca_utils import read_header
from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
from dwca_vocab_utils import vocabheader
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_terms import vocabfieldlist
import os
import logging
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

def vocab_appender(options):
    ''' Given a set of distinct key values for a given term, append any not already in the 
        given vocabulary file as new entries.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory to work in (optional)
        vocabfile - full path to the file containing the vocabulary (required)
        checkvaluelist - a list of candidate key values to append (optional)
        key - list of fields to extract from the input file (required)
        separator - string to use as the value separator in the string (default '|')
    returns a dictionary with information about the results
        workspace - path to a directory worked in
        vocabfile - full path to the file containing the vocabulary to append to
        addedvalues - new key values added to the vocabulary file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    # print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'vocabfile', 'addedvalues', 'success', 'message', \
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
    vocabfile = None
    checkvaluelist = None
    key = None
    separator = '|'

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        key = options['key']
    except:
        pass

    if key is None or len(key)==0:
        message = 'No key given. %s' % __version__
        returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        separator = options['separator']
    except:
        pass

    try:
        checkvaluelist = options['checkvaluelist']
    except:
        pass

    if checkvaluelist is None or len(checkvaluelist)==0:
        message = 'No values to check. %s' % __version__
        returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        pass

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given.' % __version__
        returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # If vocab file doesn't exist, create it with a header consisting of fieldnames
    # constructed from key
    isfile = os.path.isfile(vocabfile)

    dialect = csv_file_dialect(vocabfile)
    fieldnames = vocabheader(key)

    if not isfile:
        writevocabheader(vocabfile, fieldnames, dialect)

    filesize = os.stat(vocabfile).st_size
    # If file is empty, recreate is with a header consisting of fieldnames
    if filesize == 0:
        writevocabheader(vocabfile, fieldnames, dialect)

    # Now we should have a vocab file in utf-8 with a header at least
    header = read_header(vocabfile, dialect, 'utf-8')

    # The header for the values we are trying to add has to match the header for the 
    # vocabulary file. If not, the vocabulary structure will be compromised.
    if fieldnames != header:
        message = 'header for new values:\n%s\n' % fieldnames
        message += 'does not match vocabulary file header: %s\n' % header
        message += '%s' % __version__
        returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if key != header[0]:
        message = 'key in the header (%s)' % header[0]
        message += ' does not match vocabulary-specified key: %s\n' % key
        message += '%s' % __version__
        returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    addedvalues = distinct_vocabs_to_file(vocabfile, checkvaluelist, key=key)

    success = True

    # Add artifacts to the output dictionary if all went well
    s = '%s_vocab_file' % key
    artifacts[s] = vocabfile

    returnvals = [workspace, vocabfile, addedvalues, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)
    
def _getoptions():
    '''Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the vocabulary file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'list of potential values to add to vocabulary (required)'
    parser.add_argument("-c", "--checkvaluelist", help=help)

    help = 'string that separates fields in the key (optional)'
    parser.add_argument("-k", "--key", help=help)

    help = 'field with the distinct values in the vocabulary file (required)'
    parser.add_argument("-s", "--separator", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    theList=options.checkvaluelist
    key=options.key
    separator = ','
    checkvaluelist=[subs.strip() for subs in str(theList).split(separator)]

    if options.vocabfile is None or len(options.vocabfile)==0 \
        or theList is None or len(theList)==0 or key is None or len(key)==0:
        s =  'syntax:\n'
        s += 'python vocab_appender.py'
        s += ' -w ./workspace'
        s += ' -v ./workspace/dwcgeography.txt'
        s += ' -c "Oceania|United States|US|Hawaii|Honolulu|Honolulu'
        s += '|North Pacific Ocean|Hawaiian Islands|Oahu, '
        s += '|United States||WA|Chelan Co.||||"'
        s += ' -k "continent|country|countrycode|stateprovince|'
        s += 'county|municipality|waterbody|islandgroup|island"'
        s += ' -s |'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['vocabfile'] = options.vocabfile
    optdict['checkvaluelist'] = checkvaluelist
    optdict['key'] = options.key
    optdict['separator'] = options.separator
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of key to vocab file
    response=vocab_appender(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
