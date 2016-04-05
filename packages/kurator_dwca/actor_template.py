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
__version__ = "actor_template.py 2016-02-22T16:52-03:00"

# Imports
from optparse import OptionParser
from dwca_utils import response
from dwca_utils import term_rowcount_from_file
import os.path
import json

# This is a template for a python Kurator actor

# Actor Description
# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/term_counter.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv -p t=year
#
# or as a command-line script.
# Example:
#
# python term_counter.py -i ../../data/eight_specimen_records.csv -t country

# Functions
def term_counter(inputs_as_json):
    """Decription of what actor does
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
    returns JSON string with information about the results
        output - full path to the input file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['output', 'success', 'message']

    # outputs
    output = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputfile = inputs['inputfile']
    except:
        inputfile = None

    # Check for fail conditions
    if inputfile is None:
        message = 'No input file given'
        returnvals = [output, success, message]
        return response(returnvars, returnvals)
        
    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [output, success, message]
        return response(returnvars, returnvals)

    # Main body of the actor
    rowcount = term_rowcount_from_file(inputfile, termname)

    # Construct the response
    success = True
    returnvals = [rowcount, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Input file description",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Output file description",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    outputfile = options.outputfile

    if inputfile is None or outputfile is None:
        print 'syntax: python term_counter.py -i ../../data/eight_specimen_records.csv -o ./workspace/outputfile.txt'
        return

    # Construct the actor input JSON
    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['outputfile'] = inputfile

    # Run the actor with the given inputs
    response=json.loads(term_counter(json.dumps(inputs)))
#    print 'response: %s' % response

if __name__ == '__main__':
    main()
