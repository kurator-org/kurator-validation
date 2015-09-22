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
__version__ = "vocab_appender.py 2015-09-13T10:44:40-07:00"

from optparse import OptionParser
from dwca_utils import split_path
from dwca_utils import print_dialect_properties
from vocab_loader import vocab_loader
from dwcaterms import vocabfieldlist
import os.path
import csv
import json
import logging

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_appender.yaml -p p=fullpath -p v=../../vocabularies/basisOfRecord.csv -p n='a, b, c'
#
# or as a command-line script.
# Example:
#
# python vocab_appender.py -i ../../vocabularies/day.csv -n '33'

# Global variable for the list of potentially new values for the term to append to the vocab file
newvaluelist = None

def vocab_appender(inputs_as_json):
    """Given a set of distinct values for a given term, append any not already in the 
    corresponding vocabulary file as new entries.
    inputs_as_json - {'fullpath':'[p]', 'newvaluelist':'[n]'} where:
    p is the full path to the vocabulary file
    n is a list of candidate term values to append
    
    returns JSON string with information about the results."""

    global newvaluelist
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']
    print 'inputs: %s fullpath: %s' % (inputs, fullpath)
    # Use the newvaluelist from the input JSON, if it exists. 
    # If it comes from inputs[], it should be a list. If it comes from the global 
    # variable, it will be a string
    print 'newvaluelist: %s' % newvaluelist
    if newvaluelist is None:
        try:
            # thelist should be a list
            newvaluelist = inputs['newvaluelist']
            print 'try newvaluelist: %s' % newvaluelist
#            newvaluelist=[subs.strip() for subs in str(thelist).split(',')]
        except:
            print 'No newvaluelist given.'
            return None
    else:
        # newvaluelist should be a string
        thelist = newvaluelist
        if str(newvaluelist).find(',')>0:
            newvaluelist=[subs.strip() for subs in thelist.split(',')]
        else:
            newvaluelist=[str(newvaluelist)]

    dialect = csv.excel
    dialect.lineterminator='\r'
    
    isfile = os.path.isfile(fullpath)
    if not isfile:
        with open(fullpath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, dialect=dialect, 
                quoting=csv.QUOTE_ALL, fieldnames=vocabfieldlist)
            writer.writeheader()

    loader_params = {}
    loader_params['fullpath'] = fullpath
    vdict=json.loads(vocab_loader(json.dumps(loader_params)))
    logging.debug('Extractor response: %s' % dict)

    checklist=[]
    addedvalues=[]
    for t in newvaluelist:
        checklist.append(t)
    if len(checklist)>0:
        for t in checklist:
            if vdict.has_key(t) or t=='':
                newvaluelist.remove(t)

    with open(fullpath, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, quoting=csv.QUOTE_ALL, 
            fieldnames=vocabfieldlist)
        for term in newvaluelist:
            if term is not None and term!='':
                logging.debug('Writing %s to file %s' % (term, fullpath))
                writer.writerow({'verbatim':term, 'standard':'', 'checked':0 })

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['addedvalues']
    returnvals = [newvaluelist]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    newvaluelist = None

    print 'Appender response: %s' % response
    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to store vocabs",
                      default=None)
    parser.add_option("-n", "--newvaluelist", dest="newvaluelist",
                      help="List of new values to add to the vocab",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="The level at which to log",
                      default='INFO')
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    loglevel = options.loglevel
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
    logging.basicConfig(level=logging.DEBUG)
    fullpath = options.inputfile
    thelist=options.newvaluelist
    newvaluelist=[subs.strip() for subs in str(thelist).split(',')]
    print 'newvaluelist: %s' % newvaluelist
    if fullpath is None:
        print "syntax: python vocab_appender.py -i ../../vocabularies/basisOfRecord.csv -n 'a, b, c'"
        return
    
    inputs = {}
    inputs['fullpath'] = fullpath
    inputs['newvaluelist'] = newvaluelist
    print 'inputs: %s' % inputs
    print 'json.dumps(inputs): %s' % json.dumps(inputs)
    # Append distinct values of to vocab file
    response=json.loads(vocab_appender(json.dumps(inputs)))

#    print 'Response: %s' % response
    logging.info('To file %s, added new values: %s' % (fullpath, response['addedvalues']))

if __name__ == '__main__':
    """ Demo of vocab_appender"""
    main()
