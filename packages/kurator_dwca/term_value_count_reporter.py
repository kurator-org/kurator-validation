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
__version__ = "term_value_count_reporter.py 2016-09-20T11:56+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_dialect
from dwca_utils import tsv_dialect
from dwca_utils import extract_value_counts_from_file
import logging
import os
import csv
import uuid
import argparse

def term_value_count_reporter(options):
    """Extract a list of the distinct values of a given term in a text file along with 
       the number of times each occurs.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        format - output file format (e.g., 'csv' or 'txt') (optional)
        termlist - list of fields from which to extract values from the 
            input file (required)
        separator - string that separates the values in terms (e.g., '|') 
            (optional; default '|')
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    # print '%s options: %s' % (__version__, options)

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
    format = None
    success = False
    message = None

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given in %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if the input file is at the absolute path or in the workspace.
    if os.path.isfile(inputfile) == False:
        if os.path.isfile(workspace+'/'+inputfile) == True:
            inputfile = workspace+'/'+inputfile
        else:
            message = 'Input file %s not found' % inputfile
            returnvals = [workspace, outputfile, success, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        termlist = options['termlist']
    except:
        termlist = None

    if termlist is None or len(termlist)==0:
        message = 'No field list given in %s.' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)

    try:
        separator = options['separator']
    except:
        separator = '|'

    try:
        format = options['format']
    except:
        format = None

    if format is None:
        format = 'csv'

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    rootname = ''
    termname = ''
    n = 0
    for f in termlist:
        if n == 0:
            rootname += f
            termname += f
            n = 1
        else:
            rootname += '_'+f
            termname += separator+f
    if outputfile is None or len(outputfile)==0:
        outputfile = '%s_count_report_%s.%s' % (rootname, str(uuid.uuid1()), format)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    # Get the list of values for the field given by termname along with their counts.
    counts = extract_value_counts_from_file(inputfile, termlist, separator=separator)
    # print 'counts: %s' % counts

    #Try to create the report for the term value counts.
    success = term_value_count_report(outputfile, counts, termname=termname, format=format)
    if success==True:
        s = '%s_count_report_file' % rootname
        artifacts[s] = outputfile
    else:
        message = 'term_count_report() failed, check term name and required parameters.'
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def term_value_count_report(reportfile, termcountlist, termname='value', format=None):
    """Write a report of the counts of values for the term.
    parameters:
        reportfile - full path to the output report file
        termcountlist - list of terms with counts (required)
        termname - name of the term for which counts were made (optional; default 'value')
        format - string signifying the csv.dialect of the report file ('csv' or 'txt')
    returns:
        success - True if the report was written, else False
    """
    if reportfile is None or len(reportfile)==0:
        logging.debug('No report file given in term_count_report()')
        return False

    if termcountlist is None or len(termcountlist)==0:
        logging.debug('No term count list given in term_count_report()')
        return False

    if format=='csv' or format is None:
        dialect = csv_dialect()
    else:
        dialect = tsv_dialect()

    countreporttermlist = [termname, 'count']

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=countreporttermlist)
        writer.writeheader()

    if os.path.isfile(reportfile) == False:
        logging.debug('reportfile: %s not created' % reportfile)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=countreporttermlist)
        for item in termcountlist:
            writer.writerow({termname:item[0].encode('utf-8'), 'count':item[1] })
    return True

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = "termlist (required)"
    parser.add_argument("-t", "--term list", help=help)

    help = "separator (optional)"
    parser.add_argument("-s", "--separator", help=help)

    help = 'report file format (e.g., csv or txt) (optional)'
    parser.add_argument("-f", "--format", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax:\n'
        s += 'python term_value_count_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermcountout.txt'
        s += ' -w ./workspace'
        s += ' -t year'
        s += ' -f csv'
        print '%s' % s
        s += 'python term_value_count_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermcountout.txt'
        s += ' -w ./workspace'
        s += ' -t "country|stateprovince"'
        s += ' -s "|"'
        s += ' -f txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termlist'] = options.termlist
    optdict['separator'] = options.separator
    optdict['workspace'] = options.workspace
    optdict['format'] = options.format
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of termname from inputfile
    response=term_value_count_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
