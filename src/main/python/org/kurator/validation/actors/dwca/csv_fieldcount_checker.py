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
__version__ = "csv_fieldcount_checker.py 2016-02-09T11:11-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
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
import json
import logging

# Global variable for the list of potentially new values for the term to append to the 
# vocab file
#checkvaluelist = None

def csv_fieldcount_checker(inputs_as_json):
    """Get the first row in a csv file where the number of fields is less than the number
       of fields in the header.
    inputs_as_json - JSON string containing inputs
        inputfile - full path to the input file
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        rowindex - the line number of the first row in the inputfile where the field
            count does not match
        row - the content of the first line in the inputfile where the field count does
            not match.
    """
    inputs = json.loads(inputs_as_json)
    inputfile = inputs['inputfile']

    firstbadrowindex = 0
    row = None
    result = csv_field_checker(inputfile)
    if result is not None:
        firstbadrowindex = result[0]
        row = result[1]
    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['firstbadrowindex', 'row', 'success']
    returnvals = [firstbadrowindex, row, True]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
 #   checkvaluelist = None
    return json.dumps(response)
    
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
