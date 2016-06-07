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
__version__ = "term_recommendation_reporter.py 2016-06-07T14:06-03:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import matching_vocab_dict_from_file
from dwca_vocab_utils import term_values_recommended
from dwca_vocab_utils import not_in_list
from dwca_vocab_utils import keys_list
from report_utils import term_recommendation_report
import os.path
import logging
import argparse

def term_recommendation_reporter(options):
    """Report a list of recommended standardizations for the values of a given term in
       an input file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        vocabfile - full path to the vocabulary file (required)
        outputfile - name of the output file, without path (optional)
        termname - the name of the term for which to find standard values (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    outputfile = None
    success = False
    message = None

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
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(vocabfile) == False:
        message = 'Vocab file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
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

    if checklist is None or len(checklist)==0:
        message = 'No values of %s from %s' % (termname, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of checklist values from the vocabfile
    matchingvocabdict = matching_vocab_dict_from_file(checklist, vocabfile)

    if matchingvocabdict is None or len(matchingvocabdict)==0:
        message = 'No matching values of %s from %s found in %s' % \
            (termname, inputfile, vocabfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = term_values_recommended(matchingvocabdict)

    if recommended is None or len(recommended)==0:
        message = 'Vocabulary %s has no recommended values for %s from %s' % \
            (vocabfile, termname, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # TODO: Use Allan's DQ report framework
    # Validation, Improvement, Measure
    # Create a series of term reports
    success = term_recommendation_report(outputfile, recommended)

    matchingvocablist = keys_list(matchingvocabdict)
    newvalues = not_in_list(matchingvocablist, checklist)

    if outputfile is not None and not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s' % outputfile
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = '%s_recommendation_report_file' % termname
    artifacts[s] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'full path to the vocab file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0 or \
       options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax:\n'
        s += 'python term_recommendation_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/country.txt'
        s += ' -w ./workspace'
        s += ' -o testtermrecommendationout.txt'
        s += ' -t country'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=term_recommendation_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
