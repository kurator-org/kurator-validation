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
__version__ = "text_file_splitter.py 2015-09-02T21:50:29+02:00"

from optparse import OptionParser
from dwca_utils import split_path
import os.path
import uuid
import logging

def text_file_splitter(fullpath, chunksize, workspace):
    """Split a text file into chunks with headers. Put the chunk files in the workspace"""
    if not os.path.isfile(fullpath):
        return None, None, None

    # Open the file in universal mode
    input = open(fullpath, 'rU')

    path, fileext, filepattern = split_path(fullpath)
    
    # Get the first line of the file as the header
    header=input.next()

    # dest will be used for the chunk files
    dest = None
    count = 0
    at = 0

    # Iterate though the entire input file
    for line in input:
        # For the first line and every multiple of subsequent max_chunk_length lines
        if count % chunksize == 0:
            # Close the old chunk file, if there is one
            if dest:
                dest.close()
            # Open a new chunk file to write the next lines into, with a header
            destfile=workspace+filepattern+'-'+str(at)+'.'+fileext
            dest = open(destfile, 'w')
            dest.write(header)
            at += 1
        # Write a line to the current chunk and keep going
        dest.write(line)
        count += 1

    # Close the last chunk file
    if dest:
        dest.close()

    # Successfully completed the mission
    # Return the file pattern of the file chunked and the number of chunks created
    return filepattern, fileext, at
    
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
    chunksize = options.chunksize
    try:
        chunksize=int(str(chunksize))
    except:
        chunksize=1000
    if inputfile is None:
        print 'syntax: text_file_splitter.py -i inputfile -w workspace'
        return
    if workspace is None:
        workspace = './'
    
    # Split text file into chucks
    pattern, ext, chunks=text_file_splitter(inputfile, chunksize, workspace)

    print 'File %s.%s chunked into %s chunks of %s or less records, with headers.' \
        % (pattern, ext, chunks, chunksize)

if __name__ == '__main__':
    """ Demo of text_file_splitter"""
    main()
