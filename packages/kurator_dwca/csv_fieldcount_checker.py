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
__version__ = "csv_fieldcount_checker.py 2016-05-11T15:57-03:00"

from optparse import OptionParser
from dwca_utils import csv_field_checker
from dwca_utils import response
import os
import logging

def csv_fieldcount_checker(options):
    """Get the first row in a csv file where the number of fields is less than the number
       of fields in the header.
    options - a dictionary of parameters
        inputfile - full path to the input file (required)
    returns a dictionary with information about the results
        firstbadrowindex - the line number of the first row in the inputfile where the 
            field count does not match
        row - the content of the first line in the inputfile where the field count does
            not match.
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
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
    returnvars = ['firstbadrowindex', 'row', 'success', 'message']

    # outputs
    firstbadrowindex = 0
    row = None
    success = False
    message = None

    # inputs
    try:
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [firstbadrowindex, row, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [firstbadrowindex, row, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    result = csv_field_checker(inputfile)
    if result is not None:
        firstbadrowindex = result[0]
        row = result[1]
        message = 'Row with incorrect number fields found.'
        returnvals = [firstbadrowindex, row, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    success = True
    returnvals = [firstbadrowindex, row, success, message]
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax: python csv_fieldcount_checker.py'
        s += ' -i ./data/tests/test_bad_fieldcount1.txt'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    print 'optdict: %s' % optdict

    # Check if any rows do not have fields matching header field count
    response=csv_fieldcount_checker(optdict)
    print 'response: %s' % response
#    logging.debug('File %s, first bad row: %s\nrow:\n%s' \
#        % (options.inputfile, response['firstbadrowindex'], response['row']))

if __name__ == '__main__':
    main()
