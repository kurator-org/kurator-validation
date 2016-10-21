#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__version__ = "term_recommendation_reporter.py 2016-10-21T13:15+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import extract_values_from_file
from dwca_vocab_utils import matching_vocab_dict_from_file
from dwca_vocab_utils import term_values_recommended
from report_utils import term_recommendation_report
from slugify import slugify
import os.path
import logging
import argparse

def term_recommendation_reporter(options):
    ''' Create a report file listing values for a given term from an input file and their 
        recommended standard values.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - path to the input file. Either full path or path within the workspace
            (required)
        outputfile - name of the output file, without path (optional)
        vocabfile - path to the vocabulary file. Either full path or path within the
           workspace (required)
        format - output file format (e.g., 'csv' or 'txt') (optional; default 'txt')
        key - the field or separator-separated fieldnames that hold the distinct values 
              in the vocabulary file (required)
        separator - string to use as the value separator in the string (default '|')
        encoding - string signifying the encoding of the input file. If known, it speeds
            up processing a great deal. (optional; default None) (e.g., 'utf-8')
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    #logging.debug( 'Started %s' % __version__ )
    #logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None
    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    vocabfile = None
    format = 'txt'
    key = None
    separator = '|'
    encoding = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if the input file is at the absolute path or in the workspace.
    if os.path.isfile(inputfile) == False:
        if os.path.isfile(workspace+'/'+inputfile) == True:
            inputfile = workspace+'/'+inputfile
        else:
            message = 'Input file %s not found. %s' % (inputfile, __version__)
            returnvals = [workspace, outputfile, True, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        pass

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if vocab file is at the absolute path or in the workspace.
    vocabfileat = None
    if os.path.isfile(vocabfile) == True:
        vocabfileat = vocabfile
    else:
        vocabfileat = workspace+'/'+vocabfile

    vocabfile = vocabfileat

    try:
        key = options['key']
    except:
        pass

    if key is None or len(key)==0:
        message = 'No key given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    ### Optional inputs ###
    try:
        separator = options['separator']
    except:
        pass

    try:
        format = options['format']
    except:
        pass

    try:
        encoding = options['encoding']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile.strip())==0:
        outputfile = '%s/%s_standardization_report_%s.%s' % \
          (workspace.rstrip('/'), slugify(key), str(uuid.uuid1()), format)
    else:
        outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get a list of distinct values of the term in the input file
    fields = key.split(separator)

    # Let extract_values_from_file figure out the dialect and encoding of inputfile.
    checklist = extract_values_from_file(inputfile, fields, separator=separator, 
        encoding=encoding)

    if checklist is None or len(checklist)==0:
        message = 'No values of %s from %s. %s' % (key, inputfile, __version__)
        returnvals = [workspace, outputfile, True, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of checklist values from the vocabfile, which is assumed to be
    # in utf-8 encoding.
    matchingvocabdict = matching_vocab_dict_from_file(checklist, vocabfile, key, 
        separator=separator, encoding='utf-8')

    if matchingvocabdict is None or len(matchingvocabdict)==0:
        message = 'No matching values of %s from %s ' % (key, inputfile)
        message += 'found in %s. %s' % (vocabfile, __version__)
        returnvals = [workspace, outputfile, True, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = term_values_recommended(matchingvocabdict)

    if recommended is None or len(recommended)==0:
        message = 'Vocabulary %s has no recommended values for %s ' % (vocabfile, key)
        message += 'from %s. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, True, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # TODO: Use Allan's DQ report framework
    # Validation, Improvement, Measure
    # Create a series of term reports
    success = term_recommendation_report(outputfile, recommended, key, format=format)

    if outputfile is not None and not os.path.isfile(outputfile):
        message = 'Failed to write results to output file %s. ' % outputfile
        message += '%s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = '%s_recommendation_report_file' % key
    artifacts[s] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'full path to the vocab file (required if constantvalues is None)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'field with the distinct values in the vocabulary file (required)'
    parser.add_argument("-k", "--key", help=help)

    help = 'string that separates fields in the key (optional)'
    parser.add_argument("-s", "--separator", help=help)

    help = 'report file format (e.g., csv or txt) (optional; default csv)'
    parser.add_argument("-f", "--format", help=help)

    help = "encoding (optional)"
    parser.add_argument("-e", "--encoding", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.key is None or len(options.key)==0 or \
       options.vocabfile is None or len(options.vocabfile)==0:
        s =  'Single field syntax:\n'
        s += 'python term_recommendation_reporter.py'
        s += ' -w ./workspace'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testcountryrecommendation.txt'
        s += ' -v ./data/vocabularies/country.txt'
        s += ' -k country'
        s += ' -f txt'
        s += ' -e utf-8'
        s += ' -l DEBUG'
        print '%s' % s

        s =  'Multiple field syntax:\n'
        s += 'python term_recommendation_reporter.py'
        s += ' -w ./workspace'
        s += ' -i ./workflows/ws_geography_assessor/dwca_extractedoccurrences.txt'
        s += ' -o testgeographyrecommendations.txt'
        s += ' -v ./workflows/ws_geography_assessor/lookup_geography.txt'
        s += ' -k "continent|country|countryCode|stateProvince|county|municipality|waterBody|islandGroup|island"'
        s += ' -s "|"'
        s += ' -f txt'
        s += ' -e utf-8'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['key'] = options.key
    optdict['separator'] = options.separator
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['format'] = options.format
    optdict['encoding'] = options.encoding
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=term_recommendation_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
