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
__version__ = "dwc_terms_recommendation_reporter.py 2016-08-23T15:57+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
from dwca_utils import dialect_attributes
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import matching_vocab_dict_from_file
from dwca_vocab_utils import term_values_recommended
from dwca_vocab_utils import keys_list
from dwca_vocab_utils import not_in_list
from dwca_terms import controlledtermlist
from report_utils import term_recommendation_report
import os.path
import logging
import uuid
import argparse

def dwc_terms_recommendation_reporter(options):
    """Report a lists of recommended standardizations for the values of a terms in the
       Darwin Core controlled vocabularies.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        vocabdir - full path to the vocabulary directory (required)
        format - output file format (e.g., 'csv' or 'txt') (optional)
        prefix - prefix to prepend to the output report file names (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        guid - uuid appended to report files
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'guid', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    format = None
    guid = None
    prefix = None
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
        returnvals = [workspace, guid, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, guid, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabdir = options['vocabdir']
    except:
        vocabdir = None

    if vocabdir is None or len(vocabdir)==0:
        message = 'No vocabulary directory given'
        returnvals = [workspace, guid, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        prefix = options['prefix']+'_'
    except:
        prefix = None
    if prefix is None:
        prefix = ''

    try:
        format = options['format']
    except:
        format = None

    if format is None:
        format = 'csv'

    # Create a UUID for report set identification
    guid = str(uuid.uuid1())

    # Determine the dialect of the input file
    dialect = csv_file_dialect(inputfile)
    logging.debug('Input file dialect: %s' % dialect_attributes(dialect) )

    for termname in controlledtermlist:
        # Get a list of distinct values of the term in the input file
        checklist = distinct_term_values_from_file(inputfile, termname, dialect)

        print '%s checklist: %s' % (termname, checklist)

        if checklist is not None and len(checklist)>0:
            vocabfile = '%s/%s.txt' % (vocabdir.rstrip('/'), termname)
            s = 'Checklist ready for "%s"' % termname
            s += ' in dwc_terms_recommendation_reporter(): %s' % checklist
            logging.debug(s)

            # Get a dictionary of checklist values from the vocabfile
            matchingvocabdict = matching_vocab_dict_from_file(checklist, vocabfile)
            
#            print 'matching: %s' % matchingvocabdict

            if matchingvocabdict is not None and len(matchingvocabdict)>0:
                s = 'Matching vocab ready for "%s"' % termname
                s += ' in dwc_terms_recommendation_reporter(): %s' % matchingvocabdict
                logging.debug(s)

                # Get a dictionary of the recommended values from the matchingvocabdict
                recommended = term_values_recommended(matchingvocabdict)

                s = 'Recommendations ready for "%s"' % termname
                s += ' in dwc_terms_recommendation_reporter(): %s' % recommended
                logging.debug(s)

                print 'recommended: %s' % recommended

                if recommended is not None and len(recommended)>0:
                    # TODO: Use Allan's DQ report framework
                    # Validation, Improvement, Measure
                    # Create a series of term reports
                    outputfile = '%s/%s%s_standardization_report_%s.%s' % \
                      (workspace.rstrip('/'), prefix, termname, guid, format)

                    success = term_recommendation_report(outputfile, recommended, \
                        format=format)

                    if outputfile is not None and os.path.isfile(outputfile):
                        s = '%s_recommendation_report_file' % termname
                        artifacts[s] = outputfile
    success = True
    returnvals = [workspace, guid, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the vocab files (required)'
    parser.add_argument("-v", "--vocabdir", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file prefix (optional)'
    parser.add_argument("-p", "--prefix", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.vocabdir is None or len(options.vocabdir)==0:
        s =  'syntax:\n'
        s += 'python dwc_terms_recommendation_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/'
        s += ' -w ./workspace'
        s += ' -p my'
        s += ' -f csv'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabdir'] = options.vocabdir
    optdict['workspace'] = options.workspace
    optdict['prefix'] = options.prefix
    optdict['format'] = options.format
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=dwc_terms_recommendation_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
