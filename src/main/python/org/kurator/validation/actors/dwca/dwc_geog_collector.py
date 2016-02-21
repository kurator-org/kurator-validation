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
__version__ = "dwc_geog_collector.py 2016-02-21T16:53-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/dwc_geog_collector.yaml -p i=../../data/eight_specimen_records.csv -p o=../../vocabularies/dwc_geography.txt
#
# or as a command-line script.
# Example:
#
# python dwc_geog_collector.py -i ../../data/eight_specimen_records.csv -o ../../vocabularies/dwc_geography.txt

from optparse import OptionParser
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import terms_not_in_dwc
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import distinct_composite_term_values_from_file
from dwca_vocab_utils import not_in_list
from dwca_vocab_utils import geogvocabheader
from dwca_utils import read_header
from dwca_utils import clean_header
from dwca_terms import geogkeytermlist
from dwca_utils import response
import os
import csv
import json
import logging

def dwc_geog_collector(inputs_as_json):
    """Get geography unique combinations of geography from the inputfile and put any new 
        ones in the geography vocabulary file.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        vocabfile - full path to the geography vocabulary file
    returns JSON string with information about the results
        addedvalues - new values added to the geography vocabulary file
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
        vocabfile = inputs['vocabfile']
    except:
        vocabfile = None

    if inputfile is None:
        message = 'No input file given'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)
        
    if vocabfile is None:
        message = 'No vocab file given'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)
        
    dialect = vocab_dialect()
    geogkey = compose_key_from_list(geogkeytermlist)
    potentialgeogs = distinct_composite_term_values_from_file(inputfile, geogkey, '|')
#    print 'potentialgeogs: %s\n' % potentialgeogs
    existinggeogs = distinct_term_values_from_file(vocabfile, geogkey, dialect)
#    print 'existinggeogs: %s\n' % existinggeogs
    addedvalues = not_in_list(existinggeogs, potentialgeogs)
#    print 'added geog values: %s\n' % addedvalues

    # Now write the newgeogs to the geog vocab file, which has a distinct header
    # If the geog vocab file does not exist, make it
    geogheader = geogvocabheader()
    if not os.path.isfile(vocabfile):
        writevocabheader(vocabfile, geogheader, dialect)

    # Should have a vocab file now
    # If the geog vocab file header does not match
    checkheader = read_header(vocabfile, dialect)
    if checkheader != geogheader:
        message = 'header read from ' + vocabfile + 'does not match geogvocabheader'
        returnvals = [addedvalues, success, message]
        return response(returnvars, returnvals)

    # Add the new geogs to the geog vocab file
    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=geogheader)
        for term in addedvalues:
            writer.writerow({geogkey:term, 'standard':'', 'checked':0 })
    success = True

#    print 'header from %s:\n%s' % (vocabfile, checkheader)
#    print 'geog header:\n%s' % geogheader

    returnvals = [addedvalues, success, message]
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for geog values",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Geog vocab file",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    vocabfile = options.outputfile

    if inputfile is None or vocabfile is None:
        print "syntax: python dwc_geog_collector.py -i ../../data/eight_specimen_records.csv -o ../../vocabularies/dwc_geography.txt"
        return
    
    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['vocabfile'] = vocabfile

    # Append distinct values of to vocab file
    response=json.loads(dwc_geog_collector(json.dumps(inputs)))
    print 'response: %s' % response
    logging.debug('To file %s, added new values: %s' % (inputfile, response['addedvalues']))

if __name__ == '__main__':
    main()
