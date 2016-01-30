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
__version__ = "vocab_appender.py 2016-01-29T18:01-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_appender.yaml -p v=vocabfile -p v=./workspace/basisOfRecord.csv -p n='preservedspecimen, voucher, fossil'
#
# or as a command-line script.
# Example:
#
# python vocab_appender.py -v ../../vocabularies/day.csv -n '33'

from optparse import OptionParser
from dwca_utils import vocab_dialect
from dwca_utils import distinct_vocabs_to_file
from dwca_terms import vocabfieldlist
import json
import logging

# Global variable for the list of potentially new values for the term to append to the 
# vocab file
checkvaluelist = None

def vocab_appender(inputs_as_json):
    """Given a set of distinct values for a given term, append any not already in the 
    corresponding vocabulary file as new entries.
    inputs_as_json - JSON string containing inputs
        vocabfile - full path to the file containing the vocabulary
        checkvaluelist - a list of candidate term values to append to the vocabulary file
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        addedvalues - new values added to the vocabulary file
    """
    inputs = json.loads(inputs_as_json)
    vocabfile = inputs['vocabfile']

    # Use the checkvaluelist from the input JSON, if it exists. 
    # If it comes from inputs[], it should be a list. If it comes from the global 
    # variable, it will be a string
    # try to get the variable from inputs_as_json
    try:
        valuelist = inputs['checkvaluelist']
    except:
        theList = checkvaluelist
        if str(checkvaluelist).find(',')>0:
            valuelist=[subs.strip() for subs in thelist.split(',')]
        else:
            valuelist=[str(checkvaluelist)]

    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(vocabfile, valuelist, dialect)

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['addedvalues', 'success']
    returnvals = [addedvalues, True]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    checkvaluelist = None
    return json.dumps(response)
    
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
    global checkvaluelist
    options = _getoptions()
    vocabfile = options.vocabfile
    thelist=options.checkvaluelist
    checkvaluelist=[subs.strip() for subs in str(thelist).split(',')]
    print 'checkvaluelist: %s' % checkvaluelist
    if vocabfile is None:
        print "syntax: python vocab_appender.py -v ./workspace/basisOfRecord.csv -n 'preservedspecimen, voucher, fossil'"
        return
    
    inputs = {}
    inputs['vocabfile'] = vocabfile
    inputs['checkvaluelist'] = checkvaluelist

    print 'inputs: %s' % inputs
    print 'json.dumps(inputs): %s' % json.dumps(inputs)

    # Append distinct values of to vocab file
    response=json.loads(vocab_appender(json.dumps(inputs)))

    logging.debug('To file %s, added new values: %s' % (vocabfile, response['addedvalues']))

if __name__ == '__main__':
    main()
