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
__version__ = "vocab_loader.py 2015-09-13T12:11:52-07:00"

from optparse import OptionParser
from dwca_utils import split_path
from dwca_utils import print_dialect_properties
from dwcaterms import vocabfieldlist
import os.path
import csv
import json
import logging

# Example:
#
# python vocab_loader.py -i ../../vocabularies/month.csv

def vocab_loader(inputs_as_json):
    """Load a dict of the distinct values of a vocabulary term from a text file.
    inputs_as_json - {'fullpath':'[p]'} where:
    p is the full path to the vocabulary file
    
    returns JSON string with information about the results."""
    
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']

    if not os.path.isfile(fullpath):
        return None

    dict={}
    dialect = csv.excel
    with open(fullpath, 'rU') as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, quoting=csv.QUOTE_ALL, 
            fieldnames=vocabfieldlist)
        i=0
        for row in dr:
            # Skip the header row.
            if i>0:
                verbatim=row['verbatim']
                standard=row['standard']
                checked=row['checked']
                dict[verbatim]=[standard, checked]
            i+=1

    return json.dumps(dict)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to mine for vocab values",
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

    if fullpath is None:
        print 'syntax: python vocab_loader.py -i ../../vocabularies/month.csv'
        return
    
    inputs = {}
    inputs['fullpath'] = fullpath
    
    # Get distinct values of termname from inputfile
    response=json.loads(vocab_loader(json.dumps(inputs)))

#    print 'Response: %s' % response
    logging.info('Loaded from vocabulary file %s: %s' %
        (fullpath, response) )

if __name__ == '__main__':
    """ Demo of vocab_loader"""
    main()
