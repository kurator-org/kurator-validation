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
__version__ = "vocab_extractor.py 2015-09-13T10:48:39-07:00"

from optparse import OptionParser
from dwca_utils import split_path
from dwca_utils import print_dialect_properties
import os.path
import csv
import json
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_extractor.yaml -p p=fullpath -p v=../../data/eight_specimen_records.csv -p t=country
#
# or as a command-line script.
# Example:
#
# python vocab_extractor.py -i ../../data/eight_specimen_records.csv -t country

# The name of the term for which the distinct values are sought
termname = None

def vocab_extractor(inputs_as_json):
    """Extract a list of the distinct values of a given term in a text file.
    inputs_as_json - {'fullpath':'[p]', 'termname':'[t]'} where:
    p is the full path to the file from which to extract
    t is the name of the term for which to extract values
    
    returns JSON string with information about the results."""
    
    global termname
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']
    # Use the termname from the input JSON, if it exists
    try:
        termname = inputs['termname']
    except:
        # Otherwise use the global value, if it exists
        if termname is None:
            return None

    if not os.path.isfile(fullpath):
        return None

    valueset = set()
    dialect=csv.excel
#    print_dialect_properties(dialect)
    
    # Iterate over the file rows to get the values of the term
    with open(fullpath, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect)
        header=dr.fieldnames
        i=0
        for t in header:
            header[i]=header[i].strip()
            i+=1
        if termname not in header:
            return None
        for row in dr:
            v=row[termname]
            valueset.add(v)

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['valueset']
    returnvals = [list(valueset)]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    termname = None

    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-t", "--termname", dest="termname",
                      help="Name of the term for which distinct values are sought",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="The level at which to log",
                      default='INFO')
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    loglevel = options.loglevel
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
    fullpath = options.inputfile
    local_termname = options.termname

    if fullpath is None or local_termname is None:
        print 'syntax: python vocab_extractor.py -i ../../data/eight_specimen_records.csv -t basisOfRecord'
        return
    
    inputs = {}
    inputs['fullpath'] = fullpath
    inputs['termname'] = local_termname
    
    # Get distinct values of termname from inputfile
    response=json.loads(vocab_extractor(json.dumps(inputs)))

#    print 'Response: %s' % response
    logging.info('File %s mined for values of %s. Results: %s' %
        (fullpath, local_termname, response['valueset']) )

if __name__ == '__main__':
    """ Demo of vocab_extractor"""
    main()
