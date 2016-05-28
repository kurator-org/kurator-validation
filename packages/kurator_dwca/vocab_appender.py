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
__version__ = "vocab_appender.py 2016-05-27T21:25-03:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
import os
import logging
import argparse

def vocab_appender(options):
    """Given a set of distinct values for a given term, append any not already in the 
       corresponding vocabulary file as new entries.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        vocabfile - full path to the file containing the vocabulary (required)
        checkvaluelist - list of candidate term values to append to the vocabulary 
            file (optional)
    returns a dictionary with information about the results
        vocabfile - full path to the file containing the vocabulary
        addedvalues - new values added to the vocabulary file
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
        checkvaluelist = options['checkvaluelist']
    except:
        checkvaluelist = None
    
    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(vocabfile, checkvaluelist, dialect)
    success = True

    # Prepare the response dictionary
    returnvals = [vocabfile, addedvalues, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the vocabulary file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'list of potential values to add to vocabulary (optional)'
    parser.add_argument("-c", "--checkvaluelist", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    separator = ','
    theList=options.checkvaluelist
    checkvaluelist=[subs.strip() for subs in str(theList).split(separator)]

    if options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax:\n'
        s += 'python vocab_appender.py'
        s += ' -v ./data/vocabularies/basisOfRecord.txt'
        s += ' -c "preservedspecimen, voucher, fossil"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['vocabfile'] = options.vocabfile
    optdict['checkvaluelist'] = checkvaluelist
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of term to vocab file
    response=vocab_appender(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
