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
__version__ = "vocab_composite_extractor.py 2016-02-02T12:31-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_composite_extractor.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv -p c="continent,country,stateProvince,county,municipality,island,islandGroup,waterbody"
#
# or as a command-line script.
# Example:
#
# python vocab_composite_extractor.py -i ../../data/eight_specimen_records.csv -c "continent,country,stateProvince,county,municipality,island,islandGroup,waterbody"

from optparse import OptionParser
from dwca_utils import split_path
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import distinct_composite_term_values_from_file
import os.path
import csv
import json
import logging

# The order-dependent, separator-separated string of term names in the term composite for 
# which the distinct values are sought. Term names may not contain the separator, but 
# content may.
termcomposite = None

def vocab_composite_extractor(inputs_as_json):
    """Extract a list of the distinct values of a given termcomposite in a text file.    
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the file containing the distinct values to extract
        termcomposite - an ordered-dependent list of terms for which to extract values. 
            Example for a geography key: 
    "continent|country|stateprovince|county|municipality|island|islandgroup|waterbody"

    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        list(valueset) - a list of distinct values of the temcomposite in the file
    """
    global termcomposite
    inputs = json.loads(inputs_as_json)
    inputfile = inputs['inputfile']

    # Use the termcomposite from the input JSON, if it exists
    try:
        compositekey = inputs['termcomposite']
    except:
        # Otherwise use the global value, if it exists
        compositekey = termcomposite

    if compositekey is None:
        s = 'No composite term given'
        return fail_response(s)
        
    if not os.path.isfile(inputfile):
        s = 'Input file %s not found' % inputfile
        return fail_response(s)

    values = distinct_composite_term_values_from_file(inputfile, compositekey,'|')
#    print 'values: %s' % values

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['valueset', 'success']
    returnvals = [values, True]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    return json.dumps(response)
    
def fail_response(error):
    response = {}
    returnvars = ['valueset', 'success', 'error']
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
    parser.add_option("-c", "--termcomposite", dest="termcomposite",
                      help="Name of the term for which distinct values are sought",
                      default=None)
    return parser.parse_args()[0]

def main():
    global termcomposite
    options = _getoptions()
    inputfile = options.inputfile
    local_termcomposite = options.termcomposite

    if inputfile is None or local_termcomposite is None:
        print 'syntax: python vocab_composite_extractor.py -i ../../data/eight_specimen_records.csv -c "continent|country|stateprovince|county|municipality|island|islandgroup|waterbody"'
        return
    
    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['termcomposite'] = local_termcomposite
    
    # Get distinct values of termcomposite from inputfile
    response=json.loads(vocab_composite_extractor(json.dumps(inputs)))

#    print 'Response: %s' % response
    logging.info('File %s mined for values of\n%s.' % (inputfile,local_termcomposite))
    for r in response['valueset']:
        logging.info('%s' % (r) )

if __name__ == '__main__':
    main()
