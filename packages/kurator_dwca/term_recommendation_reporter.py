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
__version__ = "term_recommendation_reporter.py 2016-04-26T21:06-03:00"

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
import uuid

# Example: 
#
# kurator -f term_recommendation_reporter.yaml \
#         -p i=./data/eight_specimen_records.csv \
#         -p v=./data/vocabularies/month.txt \
#         -p workspace=../workspace/ \
#         -p o=monthreport.txt \
#         -p t=month
#
# or as a command-line script.
# Example:
#
# python term_count_reporter.py 
#        -i ./data/eight_specimen_records.csv 
#        -v ./data/vocabularies/month.txt
#        -w ./workspace/
#        -o monthreport.txt 
#        -t month

def term_recommendation_reporter(options):
    """Report a list of recommended standardizations for the values of a given term in
       an input file.
    options - a dictionary of parameters
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        vocabfile - full path to the vocabulary file (required)
        outputfile - name of the output file, without path (optional)
        termname - the name of the term for which to find standard values (required)
        loglevel - the level at which to log
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    print 'Started %s' % __version__
    print 'options: %s' % options
    # Set up logging
#     try:
#         loglevel = options['loglevel']
#     except:
#         loglevel = None
#     if loglevel is not None:
#         if loglevel.upper() == 'DEBUG':
#             logging.basicConfig(level=logging.DEBUG)
#         elif loglevel.upper() == 'INFO':        
#             logging.basicConfig(level=logging.INFO)
# 
#     logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message']

    # outputs
    workspace = None
    outputfile = None
    success = False
    message = None

    # inputs
    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None:
        workspace = './'

    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(vocabfile) == False:
        message = 'Vocab file not found'
        returnvals = [workspace, outputfile, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, success, message]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None:
        outputfile = '%s/%s_standardization_report_%s.txt' % \
          (workspace.rstrip('/'), termname, str(uuid.uuid1()))
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get a list of distinct values of the term in the input file
    dialect = csv_file_dialect(inputfile)
    checklist = distinct_term_values_from_file(inputfile, termname, dialect)
#    print 'checklist:\n%s' % checklist
#    print 'dialect:\n%s' % dialect_attributes(dialect)
    if checklist is None or len(checklist)==0:
        message = 'No values of %s from %s' % (termname, inputfile)
        returnvals = [workspace, outputfile, success, message]
        return response(returnvars, returnvals)

    # Get a dictionary of checklist values from the vocabfile
    matchingvocabdict = matching_vocab_dict_from_file(checklist, vocabfile)
#    print 'matchingvocabdict:\n%s' % matchingvocabdict
    if matchingvocabdict is None or len(matchingvocabdict)==0:
        message = 'No matching values of %s from %s found in %s' % \
            (termname, inputfile, vocabfile)
        returnvals = [workspace, outputfile, success, message]
        return response(returnvars, returnvals)

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = term_values_recommended(matchingvocabdict)
#    print 'recommended:\n%s' % recommended

    if recommended is None or len(recommended)==0:
        message = 'Vocabulary %s has no recommended values for %s from %s' % \
            (vocabfile, termname, inputfile)
        returnvals = [workspace, outputfile, success, message]
        return response(returnvars, returnvals)

    # Create a series of term reports
    # TODO: Use Allan's DQ report framework
    # Validation, Improvement, Measure
    success = term_recommendation_report(outputfile, recommended)

    matchingvocablist = keys_list(matchingvocabdict)
    newvalues = not_in_list(matchingvocablist, checklist)
    print 'checklist:\n%s' % checklist
#    print 'matchingvocablist:\n%s' % matchingvocablist
#    print 'newvalueslist:\n%s' % newvalues

    if outputfile is not None and not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s' % outputfile
        returnvals = [workspace, outputfile, success, message]
        return response(returnvars, returnvals)

    returnvals = [workspace, outputfile, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Input file to report on",
                      default=None)
    parser.add_option("-v", "--vocabfile", dest="vocabfile",
                      help="Vocab file to check against",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Outputfile for report",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term to check",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(DEBUG, INFO)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0 or \
       options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax: python term_recommendation_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/month.txt'
        s += ' -w ./workspace'
        s += ' -o testtermrecommendationout.txt'
        s += ' -t month'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['loglevel'] = options.loglevel

    # Report recommended standardizations for values of a given term from the inputfile
    response=term_recommendation_reporter(optdict)
    logging.debug('File %s checked for non-standard values of %s. Results: %s' %
        (options.inputfile, options.termname, response) )
    print 'response: %s' % response

if __name__ == '__main__':
    main()
