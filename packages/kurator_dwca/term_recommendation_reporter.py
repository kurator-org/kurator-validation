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
__version__ = "term_recommendation_reporter.py 2016-03-08T13:00-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_utils import csv_file_dialect
from dwca_utils import dialect_attributes
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import matching_vocab_dict_from_file
from dwca_vocab_utils import term_values_recommended
from dwca_vocab_utils import term_recommendation_report
from dwca_vocab_utils import not_in_list
from dwca_vocab_utils import keys_list
import os.path
import json
import logging

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/term_recommendation_reporter.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv -p t=year
#
# or as a command-line script.
# Example:
#
# python term_recommendation_reporter.py -i ../../data/eight_specimen_records.csv -v ../../vocabularies/month.txt -o ./workspace/monthreport.txt -t month

def term_recommendation_reporter(inputs_as_json):
    """Report a list of recommended standardizations for the values of a given term in
       an input file.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        outputfile - full path to the output file
        vocabfile - full path to the vocabulary file
        termname - the name of the term for which to find standardized values
    returns JSON string with information about the results
        newvalues - a list of values not found in the vocab file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['newvalues', 'success', 'message']

    # outputs
    newvalues = None
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
    try:
        vocabfile = inputs['vocabfile']
    except:
        vocabfile = None
    try:
        termname = inputs['termname']
    except:
        termname = None

    if inputfile is None:
        message = 'No input file given'
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    if vocabfile is None:
        message = 'No vocab file given'
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    if termname is None:
        message = 'No term given'
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    if not os.path.isfile(vocabfile):
        message = 'Vocab file %s not found' % vocabfile
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    # Get a list of distinct values of the term in the input file
    dialect = csv_file_dialect(inputfile)
    checklist = distinct_term_values_from_file(inputfile, termname, dialect)
#    print 'checklist:\n%s' % checklist
#    print 'dialect:\n%s' % dialect_attributes(dialect)

    # Get a dictionary of checklist values from the vocabfile
    matchingvocabdict = matching_vocab_dict_from_file(checklist, vocabfile)
#    print 'matchingvocabdict:\n%s' % matchingvocabdict

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = term_values_recommended(matchingvocabdict)
#    print 'recommended:\n%s' % recommended

    # Create a series of term reports - Use Allan's DQReport framework
    # Validation, Improvement, Measure
    success = term_recommendation_report(outputfile, recommended)

    matchingvocablist = keys_list(matchingvocabdict)
    newvalues = not_in_list(matchingvocablist, checklist)
#    print 'checklist:\n%s' % checklist
#    print 'matchingvocablist:\n%s' % matchingvocablist
#    print 'newvalueslist:\n%s' % newvalues

    if outputfile is not None and not os.path.isfile(outputfile):
        print 'outputfile: %s\ninputs:\n%s' % (outputfile, inputs)
        message = 'Failed to write results to output file %s' % outputfile
        returnvals = [newvalues, success, message]
        return response(returnvars, returnvals)

    returnvals = [newvalues, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Input file to report on",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Outputfile for report",
                      default=None)
    parser.add_option("-v", "--vocabfile", dest="vocabfile",
                      help="Vocab file to check against",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term to check",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile
    outputfile = options.outputfile
    vocabfile = options.vocabfile
    termname = options.termname

    if inputfile is None or vocabfile is None or termname is None:
        print 'syntax: python term_recommendation_reporter.py -i ../../data/eight_specimen_records.csv -v ../../vocabularies/month.txt -o ./workspace/monthreport.txt -t month'
        return

    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['outputfile'] = outputfile
    inputs['vocabfile'] = vocabfile
    inputs['termname'] = termname

    # Report recommended standardizations for values of a given term from the inputfile
    response=json.loads(term_recommendation_reporter(json.dumps(inputs)))
#    print 'response: %s' % response
    logging.debug('File %s checked for non-standard values of %s. Results: %s' %
        (inputfile, termname, response) )
    print 'response:\n%s' % response

if __name__ == '__main__':
    main()
