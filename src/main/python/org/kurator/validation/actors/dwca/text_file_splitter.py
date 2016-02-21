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
__version__ = "text_file_splitter.py 2016-02-21T19:38-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/text_file_splitter.yaml -p p=inputfile -p v=../../data/eight_specimen_records.csv  -p c=5 -p w=./workspace
#
# or as a command-line script.
# Example:
#
# python text_file_splitter.py -i ../../data/eight_specimen_records.csv -c 5 -w ./workspace

from optparse import OptionParser
from dwca_utils import split_path
from dwca_utils import response
import os.path
import json
import uuid
import logging

def text_file_splitter(inputs_as_json):
    """Split a text file into chunks with headers. Put the chunk files in the workspace
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
        workspace - the directory in which the output will be written
        chunksize - the maximum number of records in an output file
    returns JSON string with information about the results
        filepattern - the pattern for the split file names
        chunks - the number of files created from the split
        rowcount - the number of rows in the file that was split, not counting header
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['filepattern', 'chunks', 'rowcount', 'success', 'message']

    # outputs
    filepattern = None
    chunks = None
    rowcount = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputfile = inputs['inputfile']
    except:
        inputfile = None
    try:
        workspace = inputs['workspace']
    except:
        workspace = './workspace'
    try:
        chunksize = inputs['chunksize']
    except:
        chunksize = 10000

    # local variables
    path = None
    fileext = None

    if inputfile is None:
        message = 'No input file given'
        returnvals = [filepattern, chunks, rowcount, success, message]
        return response(returnvars, returnvals)

    if not os.path.isfile(inputfile):
        message = 'Input file %s not found' % inputfile
        returnvals = [filepattern, chunks, rowcount, success, message]
        return response(returnvars, returnvals)

    path, fileext, filepattern = split_path(inputfile)

    # Open the file in universal mode
    input = open(inputfile, 'rU')

    # Get the first line of the file as the header
    header=input.next()

    # dest will be used for the chunk files
    dest = None
    rowcount = 0
    chunks = 0

    # Iterate though the entire input file
    for line in input:
        # For the first line and every multiple of subsequent max_chunk_length lines
        if rowcount % chunksize == 0:
            # Close the old chunk file, if there is one
            if dest:
                dest.close()
            # Open a new chunk file to write the next lines into, with a header
            destfile=workspace+'/'+filepattern+'-'+str(chunks)+'.'+fileext
            dest = open(destfile, 'w')
            dest.write(header)
            chunks += 1
        # Write a line to the current chunk and keep going
        dest.write(line)
        rowcount += 1

    # Close the last chunk file
    if dest:
        dest.close()

    # Close the last input file
    if input:
        input.close()

    outputpattern = None
    if filepattern is not None and fileext is not None:
        outputpattern = workspace+'/'+filepattern+'-*.'+fileext

    success = True
    returnvals = [outputpattern, chunks, rowcount, success, message]
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to split",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Path for temporary files",
                      default=None)
    parser.add_option("-c", "--chunksize", dest="chunksize",
                      help="Maximum number of lines per chunk file",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    inputfile = options.inputfile
    workspace = options.workspace

    if inputfile is None:
        print 'syntax: python text_file_splitter.py -i ../../data/eight_specimen_records.csv -c 5 -w ./workspace'
        return

    if workspace is None:
        workspace = './workspace'

    try:
        chunksize = int(str(options.chunksize))
    except:
        chunksize = 10000
    
    inputs = {}
    inputs['inputfile'] = inputfile
    inputs['workspace'] = workspace
    inputs['chunksize'] = chunksize

    # Split text file into chucks
    response=json.loads(text_file_splitter(json.dumps(inputs)))
    chunks = response['chunks']
    splitrowcount = response['splitrowcount']
    print 'File %s with %s records chunked into %s chunks of %s or less rows in %s.' \
        % (inputfile, splitrowcount, chunks, chunksize, workspace)
    print 'Response: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_splitter"""
    main()
