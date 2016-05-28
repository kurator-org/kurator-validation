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
__version__ = "geog_recommendation_reporter.py 2016-05-27T06:43-43:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import read_header
from dwca_terms import geogkeytermlist
from dwca_vocab_utils import distinct_composite_term_values_from_file
from dwca_vocab_utils import compose_key_from_list
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import compose_key_from_row
from dwca_vocab_utils import compose_dict_from_key
from dwca_vocab_utils import prefix_keys
from dwca_terms import geogvocabfieldlist
import os
import csv
import logging
import uuid
import argparse

def geog_recommendation_reporter(options):
    """Report a list of recommended standardizations for distinct geography combinations
       in an input file compared to a geography lookup file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        vocabfile - full path to the vocabulary file (required)
        geogoutputfile - name of the distinct geogoutput file, without path (optional)
        geogrowoutputfile - name of the geog row output file, without path (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the geogoutputfile was written
        geogoutputfile - actual full path to the distinct geog output file
        geogrowoutputfile - actual full path to the geog row output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'geogoutputfile', 'geogrowoutputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    geogoutputfile = None
    geogrowoutputfile = None
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
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        vocabfile = options['vocabfile']
    except:
        vocabfile = None

    if vocabfile is None or len(vocabfile)==0:
        message = 'No vocab file given'
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(vocabfile) == False:
        message = 'Vocab file not found'
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    auuid = str(uuid.uuid1())
    try:
        geogoutputfile = options['geogoutputfile']
    except:
        geogoutputfile = None
    if geogoutputfile is None:
        geogoutputfile = '%s/geog_recommendation_report_%s.txt' % \
          (workspace.rstrip('/'), auuid)
    else:
        geogoutputfile = '%s/%s' % (workspace.rstrip('/'), geogoutputfile)

    try:
        geogrowoutputfile = options['geogrowoutputfile']
    except:
        geogrowoutputfile = None
    if geogrowoutputfile is None:
        geogrowoutputfile = '%s/geog_row_recommendation_report_%s.txt' % \
          (workspace.rstrip('/'), auuid)
    else:
        geogrowoutputfile = '%s/%s' % (workspace.rstrip('/'), geogrowoutputfile)

    # Get a list of distinct values of the term in the input file
    dialect = csv_file_dialect(inputfile)
    geogkey = compose_key_from_list(geogkeytermlist)
    checklist = distinct_composite_term_values_from_file(inputfile, geogkey, '|', dialect)
    logging.debug('checklist:\n%s' % checklist)

    if checklist is None or len(checklist)==0:
        message = 'No values of %s from %s' % (geogkey, inputfile)
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of matching checklist values from the vocabfile
    matchingvocabdict = matching_geog_dict_from_file(checklist, vocabfile)
    logging.debug('matchingvocabdict:\n%s' % matchingvocabdict)
    if matchingvocabdict is None or len(matchingvocabdict)==0:
        message = 'No matching values of %s from %s found in %s' % \
            (geogkey, inputfile, vocabfile)
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Get a dictionary of the recommended values from the matchingvocabdict
    recommended = geog_values_recommended(matchingvocabdict)
    logging.debug('recommended:\n%s' % recommended)

    if recommended is None or len(recommended)==0:
        message = 'Vocabulary %s has no recommended values for %s from %s' % \
            (vocabfile, termcomposite, inputfile)
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Create a series of term reports
    # TODO: Use Allan's DQ report framework
    # Validation, Improvement, Measure
    logging.debug('geogoutputfile:\n%s\nrecommended:\n%s' % (geogoutputfile, recommended))
    success = geog_recommendation_report(geogoutputfile, recommended)

    if not os.path.isfile(geogoutputfile):
        message = 'Failed to write results to output file %s' % geogoutputfile
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = 'geog_recommendation_report_file'
    artifacts[s] = geogoutputfile
    
    # Now work on the reports for individual records using the recommendations file
    # just created
    success = geog_row_recommendation_report(geogrowoutputfile, inputfile, recommended, dialect)

    if not os.path.isfile(geogrowoutputfile):
        message = 'Failed to write results to row output file %s' % geogrowoutputfile
        returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    s = 'geog_row_recommendation_report_file'
    artifacts[s] = geogrowoutputfile
    
    returnvals = [workspace, geogoutputfile, geogrowoutputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def matching_geog_dict_from_file(checklist, vocabfile, dialect=None):
    """Given a checklist of values, get matching values from a geography vocabulary file.
    parameters:
        checklist - list of values to get from the vocabfile
        vocabfile - full path to the vocabulary lookup file
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        matchingvocabdict - dictionary of complete vocabulary records matching the values 
            in the checklist
    """
    if checklist is None or len(checklist)==0:
        logging.debug('No list of values given in matching_geog_dict_from_file()')
        return None
    vocabdict = dwc_geog_dict_from_file(vocabfile, dialect)
    if vocabdict is None or len(vocabdict)==0:
        logging.debug('No vocabdict constructed in matching_geog_dict_from_file()')
        return None
    matchingvocabdict = {}
    for term in checklist:
        if term in vocabdict:
            matchingvocabdict[term]=vocabdict[term]
    return matchingvocabdict

def dwc_geog_dict_from_file(vocabfile, dialect=None):
    """Get a full geography vocabulary as a dict.
    parameters:
        vocabfile - full path to the vocabulary lookup file
        dialect - csv.dialect object with the attributes of the vocabulary lookup file
    returns:
        geogdict - dictionary of geography records
    """
    if vocabfile is None or len(vocabfile)==0:
        logging.debug('No vocab file given in dwc_geog_dict_from_file()')
        return None
    if os.path.isfile(vocabfile) == False:
        logging.debug('Vocab file %s not found in dwc_geog_dict_from_file()' % vocabfile)
        return None
    geogdict = {}
    if dialect is None:
        dialect = vocab_dialect()

    with open(vocabfile, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, fieldnames=geogvocabfieldlist)
        h = dr.next()
        for row in dr:
            rowdict = {}
            rowdict['checked']=row['checked']
            rowdict['incorrectable']=row['incorrectable']
            for field in geogkeytermlist:
                rowdict[field]=row[field]
            rowdict['error']=row['error']
            rowdict['comment']=row['comment']
            rowdict['higherGeographyID']=row['higherGeographyID']
            geogdict[row['geogkey']]=rowdict
    return geogdict

def geog_values_recommended(lookupdict):
    """Get non-standard geog values and their standard equivalents from a lookupdict
    parameters:
        lookupdict - a dictionary of lookup terms from a vocabulary
    returns:
        recommended - a dictionary of verbatim values and their recommended 
            standardized values
    """
    if lookupdict is None or len(lookupdict)==0:
        return None
    logging.debug('lookupdict:\n%s' % lookupdict)
    recommended = {}
    for key, value in lookupdict.iteritems():
        standard = ''
        for field in geogkeytermlist:
            logging.debug('key: %s value: %s field: %s' % (key, value, field))
            try:
                v = value[field]
            except:
                v = ''
            if v is None:
                v = ''
            standard += v + '|'
            standard = standard.strip('|')
        if key != standard:
            recommended[key] = value
    return recommended

def geog_recommendation_report(reportfile, recommendationdict, dialect=None):
    """Write a term recommendation report for geography.
    parameters:
        reportfile - the full path to the output report file
        recommendationdict - a dictionary of term recommendations
        dialect - a csv.dialect object with the attributes of the report file
    returns:
        success - True if the report was written, else False
    """
    if recommendationdict is None or len(recommendationdict)==0:
        logging.dbug('no recommendations to report')
        return False

    if reportfile is None or len(reportfile)==0:
        logging.dwbug('report file name not given')
        return False

    if dialect is None:
        dialect = tsv_dialect()

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=geogvocabfieldlist)
        writer.writeheader()

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=geogvocabfieldlist)
        for key, value in recommendationdict.iteritems():
            logging.debug(' key: %s value: %s' % (key, value))
            geogdict = { 'geogkey':key }
            for k in geogvocabfieldlist:
                if k != 'geogkey':
                    geogdict[k]=value[k]
            writer.writerow(geogdict)
    return True

def geog_row_recommendation_report(reportfile, recordfile, recommended, dialect=None):
    """Write a row recommendation report for geography.
    parameters:
        reportfile - the full path to the output report file
        recordfile - the full path to the input file
        recommended - dictionary of geography recommendations
        dialect - a csv.dialect object with the attributes of the report file
    returns:
        success - True if the report was written, else False
    """
    if recommended is None or len(recommended)==0:
        logging.debug('No recommendation dictionary given')
        return False

    if reportfile is None or len(reportfile)==0:
        logging.debug('Report file name not given')
        return False

    if recordfile is None or len(recordfile)==0:
        logging.debug('File name for input records not given')
        return False

    if dialect is None:
        dialect = tsv_dialect()

    sourceheader = read_header(recordfile)
    header = read_header(recordfile)
    header.append('recommendedgeography')
    # Add terms for new values of geography fields to the header
    for t in geogkeytermlist:
        header.append('new_'+t)

    geogkey = compose_key_from_list(geogkeytermlist)

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=header)
        writer.writeheader()

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=header)
            
        with open(recordfile, 'rU') as sourcefile:
            dr = csv.DictReader(sourcefile, dialect=dialect, fieldnames=sourceheader)
            for row in dr:
                key = compose_key_from_row(row, geogkey)
                if key in recommended:
                    reckey = compose_key_from_row(recommended[key], geogkey)
                    row['recommendedgeography'] = reckey
                    predict = compose_dict_from_key(reckey, geogkeytermlist)
                    addict = prefix_keys(predict)
                    
                    newrow = dict(row, **addict)
                    writer.writerow(newrow)
    return True

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'full path to the vocab file (required)'
    parser.add_argument("-v", "--vocabfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'geography recommendation output file name, no path (optional)'
    parser.add_argument("-g", "--geogoutputfile", help=help)

    help = 'geography row recommendation output file name, no path (optional)'
    parser.add_argument("-r", "--geogrowoutputfile", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    geogkey = compose_key_from_list(geogkeytermlist)

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.vocabfile is None or len(options.vocabfile)==0:
        s =  'syntax:\n'
        s += 'python geog_recommendation_reporter.py'
        s += ' -i ./data/tests/test_eight_specimen_records.csv'
        s += ' -v ./data/vocabularies/dwc_geography.txt'
        s += ' -w ./workspace'
        s += ' -g testgeogrecommendations.txt'
        s += ' -r testgeogrowrecommendations.csv'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['vocabfile'] = options.vocabfile
    optdict['workspace'] = options.workspace
    optdict['geogoutputfile'] = options.geogoutputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Report recommended standardizations for values of a given term from the inputfile
    response=geog_recommendation_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
