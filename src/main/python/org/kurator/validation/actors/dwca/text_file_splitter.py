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
__version__ = "text_file_splitter.py 2016-01-14T12:15-03:00"

from optparse import OptionParser
from dwca_utils import split_path
import os.path
import json
import uuid
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/text_file_splitter.yaml -p p=fullpath -p v=../../data/eight_specimen_records.csv  -p c=5 -p w=./workspace
#
# or as a command-line script.
# Example:
#
# python text_file_splitter.py -i ../../data/eight_specimen_records.csv -c 5 -w ./workspace

splitterchunksize=10000
splitterworkspace='./'

def text_file_splitter(inputs_as_json):
    """Split a text file into chunks with headers. Put the chunk files in the workspace
    inputs_as_json - JSON string containing "fullpath", which is the full path to the file to
    split.
    returns JSON string with information about the results."""

    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']

    try:
        chunksize = inputs['chunksize']
    except:
        chunksize = splitterchunksize

    try:
        workspace = inputs['workspace']
    except:
        workspace = splitterworkspace

    print 'text_file_splitter inputs: %s' % inputs_as_json
        
    if not os.path.isfile(fullpath):
        return None

    # Open the file in universal mode
    input = open(fullpath, 'rU')

    path, fileext, filepattern = split_path(fullpath)
    
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

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['filepattern', 'fileext', 'chunks', 'rowcount', 'workspace', 'chunksize']
    returnvals = [filepattern, fileext, chunks, rowcount, workspace, chunksize]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)
    
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
    global splitterchunksize, splitterworkspace
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    fullpath = options.inputfile
    splitterworkspace = options.workspace

    if fullpath is None:
        print 'syntax: python text_file_splitter.py -i ../../data/eight_specimen_records.csv -c 5 -w ./workspace'
        return

    if splitterworkspace is None:
        splitterworkspace = './'

    try:
        splitterchunksize = int(str(options.chunksize))
    except:
        splitterchunksize = 1000

    
    inputs = {}
    inputs['fullpath'] = fullpath
    
    # Split text file into chucks
    response=json.loads(text_file_splitter(json.dumps(inputs)))

    print 'File %s with %s records chunked into %s chunks of %s or less rows in %s.' \
        % (fullpath, response['rowcount'], response['chunks'], splitterchunksize, response['workspace'])
    print 'Response: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_splitter"""
    main()
