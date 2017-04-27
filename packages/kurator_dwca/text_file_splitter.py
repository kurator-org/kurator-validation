#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "text_file_splitter.py 2017-04-27T16:37-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import split_path
from dwca_utils import response
from dwca_utils import setup_actor_logging
import os
import uuid
import logging
import argparse

def text_file_splitter(options):
    ''' Split a text file into chunks with headers. Put the chunk files in the workspace.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - the directory in which the output will be written (optional)
        inputfile - full path to the input file (required)
        chunksize - the maximum number of records in an output file (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        filepattern - the pattern for the split file names
        chunks - the number of files created from the split
        rowcount - the number of rows in the file that was split, not counting header
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'filepattern', 'chunks', 'rowcount', 'success', 'message']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    filepattern = None
    chunks = None
    rowcount = None

    ### Establish variables ###
    workspace = './'
    inputfile = None
    termname = None
    chunksize = 10000

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, filepattern, chunks, rowcount, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if not os.path.isfile(inputfile):
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, filepattern, chunks, rowcount, success, message]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        chunksize = options['chunksize']
    except:
        pass

    path = None
    fileext = None
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
    
    # Prepare the response dictionary
    returnvals = [workspace, filepattern, chunks, rowcount, success, message]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'maximum number of lines in split files (optional)'
    parser.add_argument("-c", "--chunksize", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python text_file_splitter.py'
        s += ' -i ./data/eight_specimen_records.csv'
        s += ' -w ./workspace'
        s += ' -c 5'
        s += ' -l DEBUG'
        print '%s' % s
        return

    try:
        chunksize = int(str(options.chunksize))
    except:
        chunksize = 10000

    optdict['inputfile'] = options.inputfile
    optdict['workspace'] = options.workspace
    optdict['chunksize'] = chunksize
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Split text file into chucks
    response=text_file_splitter(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    """ Demo of text_file_splitter"""
    main()
