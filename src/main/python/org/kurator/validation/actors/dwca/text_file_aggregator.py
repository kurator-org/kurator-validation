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
__version__ = "text_file_aggregator.py 2016-01-07T17:27-03:00"

from optparse import OptionParser
from dwca_utils import read_header
from dwca_utils import composite_header
from dwca_utils import csv_file_dialect
from dwca_utils import tsv_dialect
import os
import glob
import csv
import json
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/text_file_aggregator.yaml -p i="../../data/*.txt" -p w=./workspace -p f=joinedfile.txt
#
# or as a command-line script.
# Example:
#
# python text_file_aggregator.py -i "../../data/*.txt" -w ./workspace -f joinedfile.txt

workspace = './workspace'
outputfile = 'aggregatedfile.txt'
inputdialect = None

def text_file_aggregator(inputs_as_json):
    """Join the contents of files in a given path. Headers are not assumed to be the
    same. Write a file containing the joined files with one header line in the workspace 
    under the designated joined file name.
    inputs_as_json - JSON string containing "inputpath", which is the full path to the 
    files to process.
    returns JSON string with information about the results."""
    inputs = json.loads(inputs_as_json)
    inputpath = inputs['inputpath']
    inputdialect = inputs['inputdialect']
    dialect = None
    if inputdialect == 'tsv':
        dialect = tsv_dialect()
    elif inputdialect == 'csv.excel' or inputdialect == 'csv':
        dialect = csv.excel

    compositeheader = composite_header(inputpath, dialect)
    print 'composite header:\n%s\ndialect attributes:\n%s' % (compositeheader, dialect_attributes(dialect))

    # Open a file to write the aggregated results
    destfile = workspace +'/'+ outputfile
    with open(destfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=tsv_dialect(), 
            fieldnames=compositeheader, extrasaction='ignore')
        writer.writeheader()
        files = glob.glob(inputpath)
        for file in files:
            if inputdialect is None:
                dialect = csv_file_dialect(file)
                print 'input file %s dialect: %s\nAttributes:\n%s' % (file, inputdialect, dialect_attributes(dialect))
            with open(file, 'rU') as inputfile:
                reader = csv.DictReader(inputfile, dialect=dialect)
                for line in reader:
                    try:
                        writer.writerow(line)
                    except:
                        print 'unable to write line:\n%s' % line

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['outputfile', 'compositeheader']
    returnvals = [destfile, list(compositeheader)]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)

def dialect_attributes(dialect):
    if dialect is None:
        return 'no dialect given'
    s = 'lineterminator: ' 
    if dialect.lineterminator == '\r':
        s+= '\r'
    elif dialect.lineterminator == '\n':
        s+= '\n'
    elif dialect.lineterminator == '\r\n':
        s+= '\r\n'
    else: 
        s += dialect.lineterminator

    s += '\ndelimiter: '
    if dialect.delimiter == '\t':
        s+= '\t'
    else:
        s+= dialect.delimiter

    s += '\nescapechar: ' 
    s += dialect.escapechar

    s += '\ndoublequote: '
    if dialect.doublequote == True:
        s += 'True' 
    else:
        s += 'False' 

    s += '\nquotechar: ' 
    s += dialect.quotechar

    s += '\nquoting: ' 
    if dialect.quoting == csv.QUOTE_NONE:
        s += 'csv.QUOTE_NONE'
    elif dialect.quoting == csv.QUOTE_MINIMAL:
        s += 'csv.QUOTE_MINIMAL'
    elif dialect.quoting == csv.QUOTE_NONNUMERIC:
        s += 'csv.QUOTE_NONNUMERIC'
    elif dialect.quoting == csv.QUOTE_ALL:
        s += 'csv.QUOTE_ALL'

    s += '\nskipinitialspace: ' 
    if dialect.skipinitialspace == True:
        s += 'True'
    else:
        s += 'False'

    s += '\nstrict: ' 
    if dialect.strict == True:
        s += 'True'
    else:
        s += 'False'
    return s

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
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Path to file with aggregated contents",
                      default=None)
    return parser.parse_args()[0]

def main():
    global workspace, outputfile, inputdialect
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    inputpath = options.inputpath
    if inputpath is None:
        print 'syntax: python text_file_aggregator.py -i "../../data/*.txt" -w ./workspace -o aggregatedfile.txt'
        return

    if options.workspace is not None:
        workspace = options.workspace
    
    if options.dialect is not None:
        inputdialect = options.dialect
    
    if options.outputfile is not None:
        outputfile = options.outputfile
    
    inputs = {}
    inputs['inputpath'] = inputpath
    inputs['inputdialect'] = inputdialect
    
    # Split text file into chucks
    response=json.loads(text_file_aggregator(json.dumps(inputs)))

    logging.debug('Input path: %s\nAggregated text file: %s\nComposite header:\n%s ' \
        % (inputpath, response['outputfile'], response['compositeheader']) )

if __name__ == '__main__':
    """ Demo of text_file_aggregator"""
    main()
