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
__version__ = "composite_header_constructor.py 2016-05-11T09:50-03:00"

from optparse import OptionParser
from dwca_utils import read_header
from dwca_utils import write_header
from dwca_utils import merge_headers
from dwca_utils import tsv_dialect
from dwca_utils import response
import logging

def composite_header_constructor(options):
    """Construct a header that contains the distinct column names in two input files and
       write the header to an outputfile.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile1 - full path to one of the input files (optional)
        inputfile2 - full path to the second input file (optional)
        outputfile - name of the output file, without path (required)
    returns a dictionary with information about the results
        compositeheader - header combining two inputs
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
#    print 'Started %s' % __version__
#    print 'options: %s' % options

    # Set up logging
#     try:
#         loglevel = options['loglevel']
#     except:
#         loglevel = None
#     if loglevel is not None:
#         if loglevel.upper() == 'DEBUG':
#             logging.basicConfig(level=logging.DEBUG)
#         elif loglevel.upper() == 'INFO':        
#             logging.basicConfig(level=logging.INFO)
# 
#     logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['compositeheader', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    compositeheader = None
    success = False
    message = None

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        file1 = options['inputfile1']
    except:
        file1 = None

    try:
        file2 = options['inputfile2']
    except:
        file2 = None

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given'
        returnvals = [compositeheader, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    header1 = read_header(file1)
    header2 = read_header(file2)

    compositeheader = merge_headers(header1, header2)

    # Write the resulting header into
    dialect = tsv_dialect()
    success = write_header(outputfile, compositeheader, dialect)
    if success == False:
        message = 'Header was not written.'
        returnvals = [compositeheader, outputfile, success, message, artifacts]
        return response(returnvars, returnvals)

    if compositeheader is not None:
        compositeheader = list(compositeheader)

    artifacts['composite_header_file'] = outputfile

    returnvals = [compositeheader, outputfile, success, message, artifacts]
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
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file (optional)",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.outputfile is None or len(options.outputfile)==0 or \
        ((options.file1 is None or len(options.file1)==0) and \
         (options.file2 is None or len(options.file2)==0)):
        s =  'syntax: python composite_header_constructor.py'
        s += ' -1 ./data/tests/test_tsv_1.txt'
        s += ' -2 ./data/tests/test_tsv_2.txt'
        s += ' -w ./workspace'
        s += ' -o test_compositeheader.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile1'] = options.file1
    optdict['inputfile2'] = options.file2
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict
    
    # Compose distinct field header from headers of files in inputpath
    response=composite_header_constructor(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
