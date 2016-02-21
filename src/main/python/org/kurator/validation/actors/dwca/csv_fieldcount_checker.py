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
__version__ = "csv_fieldcount_checker.py 2016-02-21T16:00:49-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/csv_fieldcount_checker.yaml -p i=../../data/eight_specimen_records.csv
#
# or as a command-line script.
# Example:
#
# python csv_fieldcount_checker.py -i ../../data/eight_specimen_records.csv

from optparse import OptionParser
from dwca_utils import csv_field_checker
from dwca_utils import response
import json
import logging

def csv_fieldcount_checker(inputs_as_json):
    """Get the first row in a csv file where the number of fields is less than the number
       of fields in the header.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
    returns JSON string with information about the results
        firstbadrowindex - the line number of the first row in the inputfile where the field
            count does not match
        row - the content of the first line in the inputfile where the field count does
            not match.
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['firstbadrowindex', 'row', 'success', 'message']

    # outputs
    firstbadrowindex = 0
    row = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputfile = inputs['inputfile']
    except:
        inputfile = None

    if inputfile is None:
        message = 'No input file given'
        returnvals = [firstbadrowindex, row, success, message]
        return response(returnvars, returnvals)

    result = csv_field_checker(inputfile)
    if result is not None:
        firstbadrowindex = result[0]
        row = result[1]
        message = 'Row with incorrect number fields found.'
        returnvals = [firstbadrowindex, row, success, message]
        return response(returnvars, returnvals)

    success = True
    returnvals = [firstbadrowindex, row, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    inputfile = options.inputfile

    if inputfile is None:
        print "syntax: python csv_fieldcount_checker.py -i ../../data/eight_specimen_records.csv"
        return
    
    inputs = {}
    inputs['inputfile'] = inputfile

    # Append distinct values of to vocab file
    response=json.loads(csv_fieldcount_checker(json.dumps(inputs)))
    print 'response: %s' % response
    logging.debug('File %s, first bad row: %s\nrow:\n%s' \
        % (inputfile, response['firstbadrowindex'], response['row']))

if __name__ == '__main__':
    main()
