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

import os.path
import logging
from optparse import OptionParser

import csv
import uuid
import subprocess

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader
from dwca.darwincore.utils import qualname as qn
from dwca.darwincore.terms import TERMS
from dwca_utils import dwca_write_core_tsv

CORE_FILE_EXTENSION='tsv'
CORE_CHUNK_SIZE=5

def dwca_splitter(dwcareader,filename,max_chunk_length):
    """Split the core of the archive into a csv file chunks."""
    if dwcareader is None or filename is None:
        return None
    
    # Create a unique identifier for the core TSV file to process
    fileid = uuid.uuid4().hex
    filepattern = '%s-%s' % (filename, uuid.uuid4().hex)
    filename = '%s.%s' % (filepattern, CORE_FILE_EXTENSION)

    # Create a tsv file from the dwca core
    dwca_write_core_tsv(dwcareader,filename)

    # Open the core TSV file
    input = open(filename, 'rU')

    # Get the first line of the TSV file as the header
    header=input.next()

    # dest will be used for the chunk files
    dest = None
    count = 0
    at = 0

    # Iterate though the entire core TSV file
    for line in input:
        # For the first line and every multiple of subsequent max_chunk_length lines
        if count % max_chunk_length == 0:
            # Close the old chunk file, if there is one
            if dest:
                dest.close()
            # Open a new chunk file to write the next lines into, with a header
            destfile=filepattern+'-'+str(at)+'.'+CORE_FILE_EXTENSION
            dest = open(filepattern+'-'+str(at)+'.'+CORE_FILE_EXTENSION, 'w')
            dest.write(header)
            at += 1
        # Write a line to the current chunk and keep going
        dest.write(line)
        count += 1

    # Close the last chunk file
    if dest:
        dest.close()

    # Successfully completed the mission
    # Return the file pattern of the TSV file chunked and the number of chunks created
    return filepattern, at
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-f", "--dwca_file", dest="dwca_file",
                      help="Darwin Core Archive file",
                      default=None)
    parser.add_option("-t", "--archive_type", dest="archive_type",
                      help="Darwin Core Archive file type. None or 'gbif'",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    if options.dwca_file is None:
        print 'syntax: dwca_splitter.py -f dwca_file'
        return
    
    # Make an appropriate reader based on whether the archive is standard or a GBIF
    # download.
    dwcareader = None
    if options.archive_type=='gbif':
        try:
            dwcareader = GBIFResultsReader(options.dwca_file)
        except Exception, e:
            logging.error('GBIF archive %s has an exception: %s ' % (options.dwca_file, e))
    else:
        dwcareader = DwCAReader(options.dwca_file)
    if dwcareader is None:
        print 'No viable archive found at %s' % options.dwca_file
        return

    # Create a TSV from the core of the archive
    # Split TSV into chucks
    pattern, chunks=dwca_splitter(dwcareader,'testout',CORE_CHUNK_SIZE)
    print 'File %s.%s chunked into %s chunks of %s or less records, with headers.' \
        % (pattern,CORE_FILE_EXTENSION, chunks, CORE_CHUNK_SIZE)
    dwcareader.close()

if __name__ == '__main__':
    """ Demo of dwca_utils functions"""
    main()
