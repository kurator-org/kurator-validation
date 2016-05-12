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
__version__ = "vocab_composite_appender.py 2016-05-11T20:46-03:00"

from optparse import OptionParser
from dwca_utils import read_header
from dwca_utils import response
from dwca_vocab_utils import makevocabheader
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import not_in_list
from dwca_terms import vocabfieldlist
import os
import csv

def vocab_composite_appender(options):
    """Given a set of distinct key values for a given term composite (a combination of 
       terms), append any not already in the corresponding vocabulary file as new entries.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        vocabfile - full path to the file containing the vocabulary (required)
        checkvaluelist - a list of candidate key values to append (optional)
        keyfields - a key made from a string of field names (required)
    returns a dictionary with information about the results
        vocabfile - full path to the file containing the vocabulary
        addedvalues - new composite key values added to the vocabulary file
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
        keyfields = options['keyfields']
    except:
        keyfields = None

    
    if keyfields is None or len(keyfields)==0:
        message = 'No key given'
        returnvals = [vocabfile, addedvalues, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        checkvaluelist = options['checkvaluelist']
    except:
        checkvaluelist = None

    if checkvaluelist is None or len(checkvaluelist)==0:
        message = 'No values to check'
        returnvals = [vocabfile, addedvalues, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # If vocab file doesn't exist, create it with a header consisting of fieldnames
    # constructed from keyfields
    
    isfile = os.path.isfile(vocabfile)
    dialect = vocab_dialect()
    fieldnames = makevocabheader(keyfields)
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
        message = 'composite header for new values does not match vocabulary file header'
        returnvals = [vocabfile, addedvalues, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if keyfields != header[0]:
        message = 'the key in the composite header does not match vocabulary file key'
        returnvals = [vocabfile, addedvalues, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    existingvalues = distinct_term_values_from_file(vocabfile, keyfields)        
    addedvalues = not_in_list(existingvalues, checkvaluelist)
#     print 'existingvalues:\n%s' % existingvalues
#     print 'checkvaluelist:\n%s' % checkvaluelist
#     print 'addedvalues:\n%s' % addedvalues
    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        for term in addedvalues:
            if term!='':
                writer.writerow({'verbatim':term, 'standard':'', 'checked':0 })

    success = True
    returnvals = [vocabfile, addedvalues, success, message]
#    logging.debug('message:\n%s' % message)
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
    parser.add_option("-k", "--keyfieldlist", dest="keyfieldlist",
                      help="Ordered list of fields that make up the key",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    theList=options.checkvaluelist
    keyfields=options.keyfieldlist
    separator = ','
    checkvaluelist=[subs.strip() for subs in str(theList).split(separator)]

    if options.vocabfile is None or len(options.vocabfile)==0 \
        or theList is None or len(theList)==0 or keyfields is None or len(keyfields)==0:
        s =  'syntax: python vocab_composite_appender.py'
        s += ' -v ./workspace/dwcgeography.txt'
        s += ' -n "Oceania|United States|US|Hawaii|Honolulu|Honolulu'
        s += '|North Pacific Ocean|Hawaiian Islands|Oahu, '
        s += '|United States||WA|Chelan Co.||||"'
        s += ' -k "continent|country|countrycode|stateprovince|'
        s += 'county|municipality|waterbody|islandgroup|island"'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['vocabfile'] = options.vocabfile
    optdict['checkvaluelist'] = checkvaluelist
    optdict['keyfields'] = keyfields
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of key to vocab file
    response=vocab_composite_appender(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
