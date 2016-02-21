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
__version__ = "darwin_cloud_collector.py 2016-02-21T16:07-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/darwin_cloud_collector.yaml -p i=../../data/eight_specimen_records.csv -p o=../../vocabularies/dwc_cloud.txt
#
# or as a command-line script.
# Example:
#
# python darwin_cloud_collector.py -i ../../data/eight_specimen_records.csv -o ../../vocabularies/dwc_cloud.txt

from optparse import OptionParser
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_utils import response
import json
import logging

def darwin_cloud_collector(inputs_as_json):
    """Get field names from inputfile and put any that are not Simple Darwin Core into 
       outputfile.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        outputfile - full path to the output file
    returns JSON string with information about the results
        addedvalues - new values added to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['addedvalues', 'success', 'comment']

    # outputs
    addedvalues = None
    success = False
    message = None

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

    if inputfile is None:
        message = 'No input file given'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)

    if outputfile is None:
        message = 'No output file given'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)

    header = clean_header(read_header(inputfile))
#    print 'cleaned header: %s\n' % header
    nondwc = terms_not_in_dwc(header)
#    print 'nondwc: %s\n' % nondwc

    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(outputfile, nondwc, dialect)
    success = True
    returnvals = [addedvalues, success, message]
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Text file to store field names",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    outputfile = options.outputfile

    if inputfile is None or outputfile is None:
        print "syntax: python darwin_cloud_collector.py -i ../../data/eight_specimen_records.csv -o ../../vocabularies/dwc_cloud.txt"
        return
    
    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['outputfile'] = outputfile

    # Append distinct values of to vocab file
    response=json.loads(darwin_cloud_collector(json.dumps(inputs)))
#    print 'response: %s' % response
    logging.debug('To file %s, added new values: %s' % (inputfile, response['addedvalues']))

if __name__ == '__main__':
    main()
