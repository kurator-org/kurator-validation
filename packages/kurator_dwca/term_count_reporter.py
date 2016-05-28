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
__version__ = "term_count_reporter.py 2016-05-27T16:23-03:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import tsv_dialect
from dwca_vocab_utils import distinct_term_counts_from_file
import logging
import os
import csv
import uuid
import argparse

def term_count_reporter(options):
    """Extract a list of the distinct values of a given term in a text file along with 
       the number of times each occurs.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the tsvfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        termname - the name of the term for which to find distinct values (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
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

    if workspace is None or len(workspace)==0:
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
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, success, message, artifacts]
#        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        outputfile = '%s_count_report_%s.txt' % (termname, str(uuid.uuid1()))
    
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    counts = distinct_term_counts_from_file(inputfile, termname)
    success = term_count_report(outputfile, counts)
    if success==True:
        s = '%s_count_report_file' % termname
        artifacts[s] = outputfile
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def term_count_report(reportfile, termcountlist, dialect=None):
    """Write a term count report.
    parameters:
        reportfile - full path to the output report file
        termcountlist - list of terms with counts (required)
        dialect - csv.dialect object with the attributes of the report file
    returns:
        success - True if the report was written, else False
    """
    if reportfile is None or len(reportfile)==0:
        logging.debug('No report file given in term_count_report()')
        return False
    if termcountlist is None or len(termcountlist)==0:
        logging.debug('No term count list given in term_count_report()')
        return False

    if dialect is None:
        dialect = tsv_dialect()

    countreportfieldlist = ['term', 'count']

    with open(reportfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=countreportfieldlist)
        writer.writeheader()

    if os.path.isfile(reportfile) == False:
        logging.debug('reportfile: %s not created' % reportfile)
        return False

    with open(reportfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, \
            fieldnames=countreportfieldlist)
        for item in termcountlist:
            writer.writerow({'term':item[0], 'count':item[1] })
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

    help = "name of the term (required)"
    parser.add_argument("-t", "--termname", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0 or \
       options.termname is None or len(options.termname)==0:
        s =  'syntax:\n'
        s += 'python term_count_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -o testtermcountout.txt'
        s += ' -w ./workspace'
        s += ' -t year'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct values of termname from inputfile
    response=term_count_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
