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
__version__ = "term_token_counter.py 2016-03-08T15:46-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_utils import term_token_count_from_file
from dwca_utils import token_report
import os.path
import json
import logging

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/term_token_counter.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv -p t=year
#
# or as a command-line script.
# Example:
#
# python term_token_counter.py -i ../../data/eight_specimen_records.csv -o outputfile.txt -t locality

def term_token_counter(inputs_as_json):
    """Get a dictionary of counts of tokens for a given term in an input file.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        outputfile - full path to the output file
        termname - the name of the term for which to count rows
    returns JSON string with information about the results
        tokens - a dictionary of tokens from the term in the inputfile
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['tokens', 'success', 'message']

    # outputs
    totalrowcount = None
    populatedrowcount = None
    success = False
    message = None
    tokens = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputfile = inputs['inputfile']
    except:
        inputfile = None
    try:
        outputfile = inputs['outputfile']
    except:
        outputfile = None
    try:
        termname = inputs['termname']
    except:
        termname = None

    if inputfile is None:
        message = 'No input file given'
        returnvals = [tokens, success, message]
        return response(returnvars, returnvals)
        
    if termname is None:
        message = 'No term given'
        returnvals = [tokens, success, message]
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [tokens, success, message]
        return response(returnvars, returnvals)

    tokens = term_token_count_from_file(inputfile, termname)
    success = token_report(outputfile, tokens)

    returnvals = [tokens, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for tokens in a term",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="File in which to put a report",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which tokens are sought",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    outputfile = options.outputfile
    termname = options.termname

    if inputfile is None or termname is None:
        print 'syntax: python term_token_counter.py -i ../../data/eight_specimen_records.csv -t locality'
        return

    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['outputfile'] = outputfile
    inputs['termname'] = termname

    # Get distinct values of termname from inputfile
    response=json.loads(term_token_counter(json.dumps(inputs)))
#    print 'response: %s' % response
    logging.debug('File %s mined for values of %s. Results: %s' %
        (inputfile, termname, response['tokens']) )

if __name__ == '__main__':
    main()
