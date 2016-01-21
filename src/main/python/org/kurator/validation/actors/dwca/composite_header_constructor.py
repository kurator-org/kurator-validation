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
__version__ = "composite_header_constructor.py 2016-01-21T12:41-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
# TODO: fix workflows and following example to match two-file input
# kurator -f workflows/composite_header_constructor.yaml -p i="../../data/*.txt" -p w=./workspace -p o=compositeheader.csv
#
# or as a command-line script.
# Example:
#
# python composite_header_constructor.py -1 "../../data/tests/test_tsv_1.txt" -2 "../../data/tests/test_tsv_2.txt" -w ./workspace -o compositeheader.txt'

from optparse import OptionParser
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import merge_headers
from dwca_utils import tsv_dialect
import os
import glob
import csv
import json
import logging

compositeheaderworkspace = './workspace'
compositeheaderfilename = 'compositeheader.tsv'

def composite_header_constructor(inputs_as_json):
    """Assess the headers of files in a given path. Construct a header that contains the
    distinct column names in input set. Write a file containing the composite header in 
    the workspace under the designated headerfilename.
    inputs_as_json - JSON string containing "inputpath", which is the full path to the 
    files to process.
    returns JSON string with information about the results."""
    inputs = json.loads(inputs_as_json)
    file1 = inputs['file1']
    file2 = inputs['file2']

    if file1 is None or len(file1) == 0 or file2 is None or len(file2) == 0:
        return None

    try:
        workspace = inputs['workspace']
    except:
        workspace = compositeheaderworkspace

    try:
        headerfilename = inputs['headerfilename']
    except:
        headerfilename = compositeheaderfilename

    header1 = read_header(file1)
    header2 = read_header(file2)

    compositeheader = merge_headers(header1, header2)

    # Open a file to write the resulting header into
    destfile = workspace +'/'+ headerfilename
    dialect = tsv_dialect()
    write_header(destfile, compositeheader, dialect)

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['compositeheaderoutputfile', 'compositeheader']
    returnvals = [destfile, list(compositeheader)]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)
 
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-1", "--file1", dest="file1",
                      help="Path to first file with header",
                      default=None)
    parser.add_option("-2", "--file2", dest="file2",
                      help="Path to second file with header",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Path for temporary files",
                      default=None)
    parser.add_option("-o", "--outputfilename", dest="outputfilename",
                      help="Name for file to hold the composite header",
                      default=None)
    return parser.parse_args()[0]

def main():
    global headerworkspace, compositeheaderfilename
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    file1 = options.file1
    file2 = options.file2
    headerworkspace = options.workspace
    compositeheaderfilename = options.outputfilename

    if file1 is None or file2 is None:
        print 'syntax: python composite_header_constructor.py -1 "../../data/tests/composite/test_tsv_1.txt" -2 "../../data/tests/composite/test_tsv_2.txt" -w ./workspace -o compositeheader.txt'
        return
     
    if headerworkspace is None:
        headerworkspace = './workspace'
    
    if compositeheaderfilename is None:
        compositeheaderfilename = 'compositeheader.tsv'
    
    inputs = {}
    inputs['file1'] = file1
    inputs['file2'] = file2
    
    # Compose distinct field header from headers of files in inputpath
    response=json.loads(composite_header_constructor(json.dumps(inputs)))

    logging.debug('Input file1: %s\nInput file2:%s\nHeader output file: %s\nComposite header:\n%s ' \
        % (file1, file2, response['compositeheaderoutputfile'], response['compositeheader']))

if __name__ == '__main__':
    """ Demo of composite_header_constructor"""
    main()
