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
__version__ = "vocab_extractor.py 2016-02-02T12:30-03:00"

from optparse import OptionParser
from dwca_utils import split_path
from dwca_vocab_utils import distinct_term_values_from_file
import os.path
import json
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_extractor.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv -p t=year
#
# or as a command-line script.
# Example:
#
# python vocab_extractor.py -i ../../data/eight_specimen_records.csv -t country

# The name of the term for which the distinct values are sought
extracttermname = None

def vocab_extractor(inputs_as_json):
    """Extract a list of the distinct values of a given term in a text file.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        termname - the name of the term for which to find distinct values
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        extractedvalues - a list of distinct values of the term in the inputfile
    """

    global extracttermname
    inputs = json.loads(inputs_as_json)
    inputfile = inputs['inputfile']

    # Use the termname from the input JSON, if it exists
    try:
        termname = inputs['termname']
    except:
        # Otherwise use the global value, if it exists
        termname = extracttermname
    if termname is None:
        s = 'No term name given'
        return fail_response(s)
        
    if not os.path.isfile(inputfile):
        s = 'Input file %s not found' % inputfile
        return fail_response(s)

    extractedvalues = distinct_term_values_from_file(inputfile, termname)

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['extractedvalues', 'success']
    returnvals = [extractedvalues, True]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    extracttermname = None

    return json.dumps(response)

def fail_response(error):
    response = {}
    returnvars = ['extractedvalues', 'success', 'error']
    returnvals = [None, False, error]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which distinct values are sought",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    termname = options.termname

    if inputfile is None or termname is None:
        print 'syntax: python vocab_extractor.py -i ../../data/eight_specimen_records.csv -t year'
        return

    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['termname'] = termname

    # Get distinct values of termname from inputfile
    response=json.loads(vocab_extractor(json.dumps(inputs)))
    print 'response: %s' % response
    logging.debug('File %s mined for values of %s. Results: %s' %
        (inputfile, termname, response['extractedvalues']) )

if __name__ == '__main__':
    main()
