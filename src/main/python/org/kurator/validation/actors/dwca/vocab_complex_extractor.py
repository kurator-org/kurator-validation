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
__version__ = "vocab_extractor_complex.py 2015-10-19T21:28:57+01:00"

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
# kurator -f workflows/vocab_complex_extractor.yaml -p p=fullpath -p v=../../data/eight_specimen_records.csv -p c="continent,country,stateProvince,county,municipality,island,islandGroup,waterbody"
#
# or as a command-line script.
# Example:
#
# python vocab_complex_extractor.py -i ../../data/eight_specimen_records.csv -c "continent,country,stateProvince,county,municipality,island,islandGroup,waterbody"

# The order-dependent, comma-separated string of term names in the term complex for which 
# the distinct values are sought. Term names may not contain commas. Content can. Content
# cannot contain the VALUE_SEPARATOR - '|' by default.
# termcomplex = None

VALUE_SEPARATOR = '|'
termcomplex = None

def make_key(alist):
    """Given a list of values, return a string consisting of the values in the 
    list separated by VALUE_SEPARATOR characters."""
    n=0
    for i in alist:
        if n==0:
            key=i
        else:
            key=key+VALUE_SEPARATOR+i
        n+=1
    return key
    
def vocab_complex_extractor(inputs_as_json):
    """Extract a list of the distinct values of a given termcomplex in a text file.
    inputs_as_json - {'fullpath':'[p]', 'termcomplex':'[c]'} where:
    p is the full path to the file from which to extract
    c is the ordered list of terms in the term complex for which to extract values
    
    Example for a geography key: 
    
    c "continent,country,stateprovince,county,municipality,island,islandgroup,waterbody"
    
    returns JSON string with information about the results."""
    
    global termcomplex
    
    
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']
    # Use the termcomplex from the input JSON, if it exists
    try:
        termcomplex = inputs['termcomplex']
    except:
        # Otherwise use the global value, if it exists
        if termcomplex is None:
            return None

    if not os.path.isfile(fullpath):
        return None

    valueset = set()
    dialect=csv.excel
#    print_dialect_properties(dialect)

    termlist = termcomplex.lower().split(',')
    
    # Iterate over the file rows to get the values of the term
    with open(fullpath, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect)
        header=dr.fieldnames
        i=0
        for t in header:
            header[i]=header[i].strip().lower()
            i+=1

        # Header list ready. Now pull out the values of all the terms in the term complex
        # for every row and add the key to the vocabulary with the values of the 
        # constituent terms.
        for row in dr:
            vallist=[]
            for t in termlist:
                try:
                    v=row[t]
                    vallist.append(v)
                except:
                    vallist.append('')
            valueset.add(make_key(vallist))

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
    termcomplex = None

    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
                      default=None)
    parser.add_option("-c", "--termcomplex", dest="termcomplex",
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
    local_termcomplex = options.termcomplex

    if fullpath is None or local_termcomplex is None:
        print 'syntax: python vocab_complex_extractor.py -i ../../data/eight_specimen_records.csv -c "continent,country,stateprovince,county,municipality,island,islandgroup,waterbody"'
        return
    
    inputs = {}
    inputs['fullpath'] = fullpath
    inputs['termcomplex'] = local_termcomplex
    
    # Get distinct values of termcomplex from inputfile
    response=json.loads(vocab_complex_extractor(json.dumps(inputs)))

#    print 'Response: %s' % response
    logging.info('File %s mined for values of\n%s.' % (fullpath,local_termcomplex))
    for r in response['valueset']:
        logging.info('%s' % (r) )

if __name__ == '__main__':
    """ Demo of vocab_extractor_complex"""
    main()
