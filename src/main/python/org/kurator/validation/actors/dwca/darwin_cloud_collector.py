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
__version__ = "darwin_cloud_collector.py 2016-02-05T17:12-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/darwin_cloud_collector.yaml -p v=vocabfile -p v=./workspace/basisOfRecord.csv -p n='preservedspecimen, voucher, fossil'
#
# or as a command-line script.
# Example:
#
# python darwin_cloud_collector.py -v ../../vocabularies/day.csv -n '33'

from optparse import OptionParser
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_vocab_utils import not_in_list
from dwca_terms import vocabfieldlist
from dwca_utils import read_header
from dwca_utils import clean_header
import json
import logging

# Global variable for the list of potentially new values for the term to append to the 
# vocab file
#checkvaluelist = None

def darwin_cloud_collector(inputs_as_json):
    """Get field names from inputfile and put any that are not Simple Darwin Core into 
       outputfile.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        outputfile - full path to the output file
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        addedvalues - new values added to the output file
    """
    inputs = json.loads(inputs_as_json)
    inputfile = inputs['inputfile']
    outputfile = inputs['outputfile']

    header = clean_header(read_header(inputfile))
#    print 'cleaned header: %s\n' % header
    nondwc = terms_not_in_dwc(header)
#    print 'nondwc: %s\n' % nondwc

    dialect = vocab_dialect()
    addedvalues = distinct_vocabs_to_file(outputfile, nondwc, dialect)
#    print 'addedvalues: %s\n' % addedvalues

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
 #   checkvaluelist = None
    return json.dumps(response)
    
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
        print "syntax: python darwin_cloud_collector.py -i ../../data/eight_specimen_records.csv -o '../../vocabularies/darwincloud.csv'"
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
