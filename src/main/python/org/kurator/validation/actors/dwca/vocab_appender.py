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
__version__ = "vocab_appender.py 2016-02-21T19:59-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/vocab_appender.yaml -p v=vocabfile -p v=./workspace/basisOfRecord.csv -p n='preservedspecimen, voucher, fossil'
#
# or as a command-line script.
# Example:
#
# python vocab_appender.py -v ../../vocabularies/day.csv -n '33'

from optparse import OptionParser
from dwca_utils import response
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_terms import vocabfieldlist
import os
import json
import logging

def vocab_appender(inputs_as_json):
    """Given a set of distinct values for a given term, append any not already in the 
    corresponding vocabulary file as new entries.
    inputs_as_json - JSON string containing inputs
        vocabfile - full path to the file containing the vocabulary
        checkvaluelist - a list of candidate term values to append to the vocabulary file
    returns JSON string with information about the results
        addedvalues - new values added to the vocabulary file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['addedvalues', 'success', 'message']

    # outputs
    addedvalues = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        vocabfile = inputs['vocabfile']
    except:
        vocabfile = None
    try:
        checkvaluelist = inputs['checkvaluelist']
    except:
        checkvaluelist = None

    if vocabfile is None:
        message = 'No vocabfile file given'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)
    
    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(vocabfile, checkvaluelist, dialect)
    success = True

    returnvals = [addedvalues, success, message]
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
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    vocabfile = options.vocabfile
    thelist=options.checkvaluelist
    checkvaluelist=[subs.strip() for subs in str(thelist).split(',')]
#    print 'checkvaluelist: %s' % checkvaluelist
    if vocabfile is None:
        print "syntax: python vocab_appender.py -v ./workspace/basisOfRecord.csv -n 'preservedspecimen, voucher, fossil'"
        return
    
    inputs = {}
    inputs['vocabfile'] = vocabfile
    inputs['checkvaluelist'] = checkvaluelist

#    print 'inputs: %s' % inputs

    # Append distinct values of term to vocab file
    response=json.loads(vocab_appender(json.dumps(inputs)))
#    print 'response: %s' % response
    logging.debug('To file %s, added new values: %s' % (vocabfile, response['addedvalues']))

if __name__ == '__main__':
    main()
