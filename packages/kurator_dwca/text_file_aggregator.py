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
__version__ = "text_file_aggregator.py 2016-02-21T19:04-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/text_file_aggregator.yaml -p i="../../data/tests/test_tsv_*.txt" -p w=./workspace -p f=joinedfile.txt -p d=tsv
#
# or as a command-line script.
# Example:
#
# python text_file_aggregator.py -i "../../data/tests/test_tsv_*.txt" -w ./workspace -f joinedfile.txt -d tsv

from optparse import OptionParser
from dwca_utils import composite_header
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
from dwca_utils import dialect_attributes
from dwca_utils import response
import os
import glob
import csv
import json
import logging

def text_file_aggregator(inputs_as_json):
    """Join the contents of files in a given path. Headers are not assumed to be the
    same. Write a file containing the joined files with one header line.
    inputs_as_json - JSON string containing inputs
        inputpath - full path to the input
        input dialect - the csv dialect of the input files ("tsv", "excel", or None)
        aggregatedfile - full path to the outputfile
    returns JSON string with information about the results
        aggregaterowcount - the number of rows in the aggregated file, not counting header
        aggregateheader - the header for the aggregated file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['aggregaterowcount', 'aggregateheader', 'success', 'message']

    # outputs
    success = False
    aggregaterowcount = None
    aggregateheader = None
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputpath = inputs['inputpath']
    except:
        inputpath = None
    try:
        aggregatedfile = inputs['aggregatedfile']
    except:
        aggregatedfile = None
    try:
        inputdialect = inputs['inputdialect']
    except:
        inputdialect = None

    if inputpath is None:
        message = 'No input path given'
        returnvals = [aggregaterowcount, aggregateheader, success, message]
        return response(returnvars, returnvals)

    if aggregatedfile is None:
        message = 'No input file given'
        returnvals = [aggregaterowcount, aggregateheader, success, message]
        return response(returnvars, returnvals)

    dialect = None
    if inputdialect == 'tsv':
        dialect = tsv_dialect()
    elif inputdialect == 'excel' or inputdialect == 'csv.excel': 
        dialect = csv.excel

    aggregateheader = composite_header(inputpath, dialect)
    aggregaterowcount = 0

    # Open a file to write the aggregated results
    with open(aggregatedfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=tsv_dialect(), 
            fieldnames=aggregateheader, extrasaction='ignore')
        writer.writeheader()
        files = glob.glob(inputpath)
        for file in files:
            if inputdialect is None:
                dialect = csv_file_dialect(file)
#                print 'input file %s dialect: %s\nAttributes:\n%s' % (file, inputdialect, dialect_attributes(dialect))
            with open(file, 'rU') as inputfile:
                reader = csv.DictReader(inputfile, dialect=dialect)
                for line in reader:
                    try:
                        writer.writerow(line)
                        aggregaterowcount += 1
                    except:
                        message = 'failed to write line:\n%s\nto file %s' % (line, file)
                        returnvals = [aggregaterowcount, aggregateheader, success, message]
                        return response(returnvars, returnvals)

    success = True
    if aggregateheader is not None:
        aggregateheader = list(aggregateheader)
    returnvals = [aggregaterowcount, aggregateheader, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputpath", dest="inputpath",
                      help="Path to files to analyze",
                      default=None)
    parser.add_option("-d", "--dialect", dest="dialect",
                      help="CSV dialect to use",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Path for temporary files",
                      default=None)
    parser.add_option("-o", "--aggregatedfile", dest="aggregatedfile",
                      help="Path to file with aggregated contents",
                      default=None)
    return parser.parse_args()[0]

def main():
    global aggregatorworkspace, aggregatedfilename, aggregatordialect
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    inputpath = options.inputpath
    aggregatorworkspace = options.workspace
    aggregatordialect = options.dialect

    if inputpath is None:
        print 'syntax: python text_file_aggregator.py -i "../../data/tests/test_tsv_*.txt" -w ./workspace -o aggregatedfile.txt -d tsv'
        return

    if aggregatorworkspace is None:
        aggregatorworkspace = './workspace'
    
    if aggregatordialect is None:
        aggregatordialect = None
    
    if aggregatedfilename is None:
        aggregatedfilename = 'aggregatedfile.txt'
    
    inputs = {}
    inputs['inputpath'] = inputpath
    inputs['aggregatedfile'] = aggregatedfilename
    inputs['workspace'] = aggregatorworkspace

    if aggregatordialect is not None:
        inputs['inputdialect'] = aggregatordialect

    # Aggregate files
    response=json.loads(text_file_aggregator(json.dumps(inputs)))

    logging.debug('Input path: %s\nAggregated text file: %s\nAggregated row count: %s\nComposite header:\n%s ' \
        % (inputpath, aggregatedfilename, response['aggregaterowcount'], response['aggregateheader']) )

if __name__ == '__main__':
    main()