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
__version__ = "term_token_reporter.py 2016-08-03T14:13+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
from dwca_utils import csv_file_encoding
from dwca_utils import read_header
from dwca_utils import read_csv_row
from dwca_utils import tsv_dialect
import os
import re
import csv
import uuid
import logging
import argparse

tokenreportfieldlist = ['token', 'rowcount', 'totalcount']

def term_token_reporter(options):
    """Get a dictionary of counts of tokens for a given term in an input file.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
        outputfile - name of the output file, without path (optional)
        termname - the name of the term for which to count rows (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output report file
        tokens - a dictionary of tokens from the term in the inputfile
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'tokens', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    workspace = None
    outputfile = None
    success = False
    message = None
    tokens = None

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
        returnvals = [workspace, outputfile, tokens, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, tokens, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        termname = options['termname']
    except:
        termname = None

    if termname is None or len(termname)==0:
        message = 'No term given'
        returnvals = [workspace, outputfile, tokens, success, message, artifacts]
        logging.debug('message: %s' % message)
        return response(returnvars, returnvals)
        
    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        outputfile = '%s_token_report_%s.txt' % (termname, str(uuid.uuid1()))
    
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    tokens = term_token_count_from_file(inputfile, termname)
    success = token_report(outputfile, tokens)
    if success==True:
        s = '%s_token_report_file' % termname
        artifacts[s] = outputfile

    returnvals = [workspace, outputfile, tokens, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def token_report(reportfile, tokens, dialect=None):
    """Write a term token report to a file.
    parameters:
        reportfile - full path to the report file (optional)
        tokens - dictionary of token occurrences (required) (see output from 
            term_token_count_from_file()
        dialect - csv.dialect object with the attributes of the report file (default None)
    returns:
        True if the report was written, otherwise False
    """
    if tokens is None or len(tokens)==0:
        logging.debug('No token dictionary given in token_report().')
        return False

    if dialect is None:
        dialect = tsv_dialect()
    
    if reportfile is not None:
        with open(reportfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=tokenreportfieldlist)
            writer.writeheader()

        if os.path.isfile(reportfile) == False:
            logging.debug('File %s not found in term_rowcount_from_file().' % reportfile)
            return False

        with open(reportfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, \
                fieldnames=tokenreportfieldlist)

            for key, value in tokens['tokenlist'].iteritems():
                logging.debug(' key: %s value: %s' % (key, value))
                writer.writerow({'token':key, 'rowcount':value['rowcount'], \
                    'totalcount':value['totalcount'] })
    else:
        # Print the report
        for key, value in tokens['tokenlist'].iteritems():
            print 'token: %s rowcount: %s totalcount: %s' % (key, value['rowcount'], \
                value['totalcount'])

    return True

def term_token_count_from_file(inputfile, termname):
    """Make a dictionary of tokens for a given term in a file along with the number of 
       times each occurs.
    parameters:
        inputfile - full path to the input file (required)
        termname - term for which to count rows (required)
    returns:
        tokens - a dictionary containing the tokens and their counts
    """
    if inputfile is None or len(inputfile) == 0:
        logging.debug('No input file given in term_token_count_from_file().')
        return 0

    if termname is None or len(termname) == 0:
        logging.debug('No term name given in term_token_count_from_file().')
        return 0

    if os.path.isfile(inputfile) == False:
        logging.debug('File %s not found in term_token_count_from_file().' % inputfile)
        return 0

    # Determine the dialect and encoding of the input file
    inputdialect = csv_file_dialect(inputfile)
    inputencoding = csv_file_encoding(inputfile)
    inputheader = read_header(inputfile, inputdialect)

    if termname not in inputheader:
        s = 'Term %s not found in file %s '
        s += 'in term_token_count_from_file().' % (termname, inputfile)
        logging.debug(s)
        return None

    rowcount = 0
    tokencount = 0
    populatedrowcount = 0
    tokens = { 'tokenlist':{} }

    for row in read_csv_row(inputfile, inputdialect, inputencoding):
        try:
            value = row[termname]
        except:
            pass

        if value is not None and len(value.strip()) > 0:
            rowdict = {}
            wordlist = re.sub("[^\w]", " ",  value).split()

            for token in wordlist:
                if token in rowdict:
                    rowdict[token]['totalcount']=rowdict[token]['totalcount']+1
                else:
                    rowdict[token]={}
                    rowdict[token]['rowcount']=1
                    rowdict[token]['totalcount']=1

            populatedrowcount += 1

            for key, value in rowdict.iteritems():
                tokenlist = tokens['tokenlist']
                if key in tokenlist:
                    tokenlist[key]['rowcount'] = \
                        tokenlist[key]['rowcount'] + value['rowcount']
                    tokenlist[key]['totalcount'] = \
                        tokenlist[key]['totalcount'] + value['totalcount']
                else:
                    tokenlist[key] = {}
                    tokenlist[key]['rowcount'] = value['rowcount']
                    tokenlist[key]['totalcount'] = value['totalcount']
        rowcount += 1
        tokencount += len(wordlist)

    tokens['rowcount']=rowcount
    tokens['tokencount']=tokencount
    tokens['input']=inputfile
    tokens['term']=termname

    return tokens

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
        s += 'python term_token_reporter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -w ./workspace'
        s += ' -o testtermtokenout.txt'
        s += ' -t locality'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['termname'] = options.termname
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Get distinct tokens in given field from inputfile
    response=term_token_reporter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
