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
__version__ = "vocab_appender.py 2016-05-11T20:29-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
import os
import logging

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
#    print 'Started %s' % __version__
#    print 'options: %s' % options

    # Set up logging
#     try:
#         loglevel = options['loglevel']
#     except:
#         loglevel = None
#     if loglevel is not None:
#         if loglevel.upper() == 'DEBUG':
#             logging.basicConfig(level=logging.DEBUG)
#         elif loglevel.upper() == 'INFO':        
#             logging.basicConfig(level=logging.INFO)
# 
#     logging.info('Starting %s' % __version__)

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
#        logging.debug('message:\n%s' % message)
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
#    logging.debug('message:\n%s' % message)
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-v", "--vocabfile", dest="vocabfile",
                      help="Text file to store vocabs",
                      default=None)
    parser.add_option("-n", "--checkvaluelist", dest="checkvaluelist",
                      help="List of new values to add to the vocab",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    separator = ','
    theList=options.checkvaluelist
    checkvaluelist=[subs.strip() for subs in str(theList).split(separator)]

    if options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax: python vocab_appender.py'
        s += ' -v ./data/vocabularies/basisOfRecord.txt'
        s += ' -n "preservedspecimen, voucher, fossil"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['vocabfile'] = options.vocabfile
    optdict['checkvaluelist'] = checkvaluelist
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of term to vocab file
    response=vocab_appender(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
