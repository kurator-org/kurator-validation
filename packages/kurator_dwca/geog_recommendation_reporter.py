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
__version__ = "geog_recommendation_reporter.py 2016-05-20T04:47-03:00"

from optparse import OptionParser
from dwca_utils import response
from dwca_utils import csv_file_dialect
from dwca_terms import geogkeytermlist
from dwca_vocab_utils import distinct_composite_term_values_from_file
from dwca_vocab_utils import matching_geog_dict_from_file
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import geog_values_recommended
from dwca_vocab_utils import geog_recommendation_report
import os
import logging
import uuid

def geog_recommendation_reporter(options):
    """Report a list of recommended standardizations for distinct geography combinations
       in an input file compared to a geography lookup file.
    options - a dictionary of parameters
        loglevel - the level at which to log (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        vocabfile - full path to the vocabulary file (required)
        outputfile - name of the output file, without path (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    logging.info( 'Started %s' % __version__ )
    logging.info( 'options: %s' % options )
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
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(vocabfile) == False:
        message = 'Vocab file not found'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None:
        outputfile = '%s/geog_recommendation_report_%s.txt' % \
          (workspace.rstrip('/'), str(uuid.uuid1()))
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get a list of distinct values of the term in the input file
    dialect = csv_file_dialect(inputfile)

    geogkey = compose_key_from_list(geogkeytermlist)

    checklist = distinct_composite_term_values_from_file(inputfile, geogkey, '|', dialect)
    
#    print 'checklist:\n%s' % checklist
    if checklist is None or len(checklist)==0:
        message = 'No values of %s from %s' % (geogkey, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of matching checklist values from the vocabfile
    matchingvocabdict = matching_geog_dict_from_file(checklist, vocabfile)
#    print 'matchingvocabdict:\n%s' % matchingvocabdict
    if matchingvocabdict is None or len(matchingvocabdict)==0:
        message = 'No matching values of %s from %s found in %s' % \
            (geogkey, inputfile, vocabfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = geog_values_recommended(matchingvocabdict)
#    print 'recommended:\n%s' % recommended

    if recommended is None or len(recommended)==0:
        message = 'Vocabulary %s has no recommended values for %s from %s' % \
            (vocabfile, termcomposite, inputfile)
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Create a series of term reports
    # TODO: Use Allan's DQ report framework
    # Validation, Improvement, Measure
#    print 'outputfile:\n%s\nrecommended:\n%s' % (outputfile, recommended)
    success = geog_recommendation_report(outputfile, recommended)

    if not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s' % outputfile
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = 'geog_recommendation_report_file'
    artifacts[s] = outputfile
    
    # Now work on the reports for individual records using the recommendations file
    # just created
    ###
    # for every row in the inputfile
    #    get the geogkey
    #    if the geogkey is in the recommended dictionary
    #        write the recomendation with record identifier and geogkey to file
    # if the file doesn't exist, something went wrong
    # add the file to the artifacts
    
    returnvals = [workspace, outputfile, success, message, artifacts]
#    logging.debug('message:\n%s' % message)
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="Input file to report on",
                      default=None)
    parser.add_option("-v", "--vocabfile", dest="vocabfile",
                      help="Vocab file to check against",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Outputfile for report",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(DEBUG, INFO)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    geogkey = compose_key_from_list(geogkeytermlist)

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax:\npython geog_recommendation_reporter.py'
        s += ' -i ./data/tests/test_eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/dwc_geography.txt'
        s += ' -w ./workspace'
        s += ' -o testgeogrecommendations.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=geog_recommendation_reporter(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
