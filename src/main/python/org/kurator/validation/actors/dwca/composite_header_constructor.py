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
__copyright__ = "Copyright 2015 President and Fellows of Harvard College"
__version__ = "composite_header_constructor.py 2015-12-28T13:59-03:00"

from optparse import OptionParser
from dwca_utils import readheader
from dwca_utils import writeheader
from dwca_utils import composite_header
from dwca_utils import csv_file_dialect
import os
import glob
import csv
import json
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/composite_header_constructor.yaml -p i="../../data/*.txt" -p w=./workspace -p o=compositeheader.csv
#
# or as a command-line script.
# Example:
#
# python composite_header_constructor.py -i "../../data/*.txt" -w ./workspace -o compositeheader.csv

headerworkspace = './workspace'
compositeheaderfilename = 'compositeheader.csv'

def composite_header_constructor(inputs_as_json):
    """Assess the headers of files in a given path headers. Construct a header that 
    contains the distinct column names in input set. Write a file containing the composite
    header in the workspace under the designated 
    inputs_as_json - JSON string containing "inputpath", which is the full path to the 
    files to process.
    returns JSON string with information about the results."""
    inputs = json.loads(inputs_as_json)
    inputpath = inputs['inputpath']

    files = glob.glob(inputpath)
    dialect = csv_file_dialect(files[0])
    compositeheader = composite_header(inputpath, dialect)

    # Open a file to write the resulting header into
    destfile = headerworkspace +'/'+ compositeheaderfilename
    writeheader(destfile, compositeheader, dialect)

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['headeroutputfile', 'compositeheader']
    returnvals = [destfile, list(compositeheader)]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputpath", dest="inputpath",
                      help="Path to files to analyze",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Path for temporary files",
                      default=None)
    parser.add_option("-o", "--headerfilename", dest="headerfilename",
                      help="Name for file to hold composite header",
                      default=None)
    return parser.parse_args()[0]

def main():
    global headerworkspace, compositeheaderfilename
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    inputpath = options.inputpath
    if inputpath is None:
        print 'syntax: python composite_header_constructor.py -i "../../data/*.txt" -w ./workspace -o compositeheader.txt'
        return
     
    if options.workspace is not None:
        headerworkspace = options.workspace
    
    if options.headerfilename is not None:
        compositeheaderfilename = options.headerfilename
    
    inputs = {}
    inputs['inputpath'] = inputpath
    
    # Split text file into chucks
    response=json.loads(composite_header_constructor(json.dumps(inputs)))

    logging.debug('Input directory: %s\nHeader output file: %s\nComposite header:\n%s ' \
        % (inputpath, response['headeroutputfile'], response['compositeheader']))

if __name__ == '__main__':
    """ Demo of composite_header_constructor"""
    main()
