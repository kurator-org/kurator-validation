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
__version__ = "vocab_appender.py 2016-08-21T13:20+02:00"

from dwca_utils import read_header
from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_vocab_utils import vocabheader
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import defaultvocabkey
from dwca_terms import vocabfieldlist
import os
import csv
import logging
import argparse

def vocab_appender(options):
    """Given a set of distinct key values for a given term, append any not already in the 
       given vocabulary file as new entries.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        vocabfile - full path to the file containing the vocabulary (required)
        checkvaluelist - a list of candidate key values to append (optional)
        key - the field name that holds the distinct values in the vocabulary file
            (optional; default None)
    returns a dictionary with information about the results
        vocabfile - full path to the file containing the vocabulary
        addedvalues - new key values added to the vocabulary file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['vocabfile', 'addedvalues', 'success', 'message']

    # outputs
    addedvalues = None
    success = False
    message = None

    # inputs
    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocabfile file given'
        returnvals = [vocabfile, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        key = options['key']
    except:
        key = defaultvocabkey

    try:
        checkvaluelist = options['checkvaluelist']
    except:
        checkvaluelist = None

    if checkvaluelist is None or len(checkvaluelist)==0:
        message = 'No values to check'
        returnvals = [vocabfile, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # If vocab file doesn't exist, create it with a header consisting of fieldnames
    # constructed from key
    
    isfile = os.path.isfile(vocabfile)
    dialect = vocab_dialect()
    fieldnames = vocabheader(key)
    if not isfile:
        writevocabheader(vocabfile, fieldnames, dialect)

    filesize = os.stat(vocabfile).st_size
    # If file is empty, recreate is with a header consisting of fieldnames
    if filesize == 0:
        writevocabheader(vocabfile, fieldnames, dialect)

    # Now we should have a vocab file with a header at least
    header = read_header(vocabfile, dialect)

    # The header for the values we are trying to add has to match the header for the 
    # vocabulary file. If not, the vocabulary structure will be compromised.
    if fieldnames != header:
        message = 'header for new values:\n%s\n' % fieldnames
        message += 'does not match vocabulary file header: %s' % header
        returnvals = [vocabfile, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if key != header[0]:
        message = 'key in the header (%s)' % header[0]
        message += ' does not match vocabulary specified key: %s' % key
        returnvals = [vocabfile, addedvalues, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    addedvalues = distinct_vocabs_to_file(vocabfile, checkvaluelist, key=key)

    success = True
    returnvals = [vocabfile, addedvalues, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the vocabulary file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'list of potential values to add to vocabulary (required)'
    parser.add_argument("-c", "--checkvaluelist", help=help)

    help = 'field with the distinct values in the vocabulary file (required)'
    parser.add_argument("-k", "--key", help=help)

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
        s += ' -v ./workspace/dwcgeography.txt'
        s += ' -c "Oceania|United States|US|Hawaii|Honolulu|Honolulu'
        s += '|North Pacific Ocean|Hawaiian Islands|Oahu, '
        s += '|United States||WA|Chelan Co.||||"'
        s += ' -k "continent|country|countrycode|stateprovince|'
        s += 'county|municipality|waterbody|islandgroup|island"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['vocabfile'] = options.vocabfile
    optdict['checkvaluelist'] = checkvaluelist
    optdict['key'] = key
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of key to vocab file
    response=vocab_appender(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
