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
__version__ = "composite_header_constructor.py 2016-02-21T14:35-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
# kurator -f workflows/composite_header_constructor.yaml -p 1="../../data/tests/test_tsv_1.txt" -p 2=../../data/tests/test_tsv_2.txt -p o="./workspace/compositeheader.txt"
#
# or as a command-line script.
# Example:
#
# python composite_header_constructor.py -1 "../../data/tests/test_tsv_1.txt" -2 "../../data/tests/test_tsv_2.txt" -w ./workspace -o "./workspace/compositeheader.txt"

from optparse import OptionParser
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import merge_headers
from dwca_utils import tsv_dialect
from dwca_utils import response
import os
import glob
import csv
import json
import logging

def composite_header_constructor(inputs_as_json):
    """Construct a header that contains the distinct column names in two input files and
       write the header to an outputfile.
    inputs_as_json - JSON string containing inputs
        inputfile1 - full path to one of the input files
        inputfile2 - full path to the second input file
        outputfile - full path to the output file
    returns JSON string with information about the results
        compositeheader - the constructed header
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['compositeheader', 'success', 'message']

    # outputs
    compositeheader = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        file1 = inputs['inputfile1']
    except:
        file1 = None
    try:
        file2 = inputs['inputfile2']
    except:
        file2 = None
    try:
        headeroutputfile = inputs['outputfile']
    except:
        headeroutputfile = None

    if headeroutputfile is None:
        message = 'No output file given'
        returnvals = [compositeheader, success, message]
        return response(returnvars, returnvals)

    header1 = read_header(file1)
    header2 = read_header(file2)

    compositeheader = merge_headers(header1, header2)

    # Write the resulting header into
    dialect = tsv_dialect()
    success = write_header(headeroutputfile, compositeheader, dialect)
    if success == False:
        message = 'Header was not written.'
        returnvals = [compositeheader, success, message]
        return response(returnvars, returnvals)

    if compositeheader is not None:
        compositeheader = list(compositeheader)

    returnvals = [compositeheader, success, message]
    return response(returnvars, returnvals)
 
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-1", "--file1", dest="file1",
                      help="Path to first file with header",
                      default=None)
    parser.add_option("-2", "--file2", dest="file2",
                      help="Path to second file with header",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Name for file to hold the composite header",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    file1 = options.file1
    file2 = options.file2
    outputfile = options.outputfile

    if file1 is None or file2 is None or outputfile is None:
        print 'syntax: python composite_header_constructor.py -1 "../../data/tests/composite/test_tsv_1.txt" -2 "../../data/tests/composite/test_tsv_2.txt" -o "./workspace/compositeheader.txt"'
        return
    
    inputs = {}
    inputs['inputfile1'] = file1
    inputs['inputfile2'] = file2
    inputs['outputfile'] = outputfile

    # Compose distinct field header from headers of files in inputpath
    response=json.loads(composite_header_constructor(json.dumps(inputs)))

    s = 'Input file1: %s\n' % file1
    s += 'Input file2: %s\n' % file2
    s += 'Header output file: %s\n' % outputfile
    s += 'Composite header:\n%s' % response['compositeheader']
    logging.debug( s )

if __name__ == '__main__':
    main()
