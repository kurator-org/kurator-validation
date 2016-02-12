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
__version__ = "vocab_composite_appender.py 2016-02-10T17:00-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocab_composite_appender.yaml -p p=fullpath -p v=../../vocabularies/basisOfRecord.csv -p n='a, b, c'
#
# or as a command-line script.
# Example:
#
# python vocab_composite_appender.py -i ../../vocabularies/day.csv -n '33'

from optparse import OptionParser
from dwca_utils import split_path
from dwca_utils import read_header
from dwca_vocab_utils import distinct_vocabs_to_file
from dwca_vocab_utils import makevocabheader
from dwca_vocab_utils import writevocabheader
#from dwca_vocab_utils import readvocabheader
from vocab_loader import vocab_loader
from dwca_terms import vocabfieldlist
import os.path
import csv
import json
import logging

# Global variable for the list of potentially new values for the term to append to the vocab file
newvaluelist = None

# def makevocabheader(keyfields):
# 	# Construct the header row for this vocabulary. Begin with a field name
# 	# equal to the keyfields variable, then add the remaining field names after
# 	# the first one from the standard vocabfieldlist.
# 	# Example:
# 	# if keyfields = 'country|stateprovince|county'
# 	# and
# 	# vocabfieldlist = ['verbatim','standard','checked']
# 	# then the header will end up as 
# 	# 'country|stateprovince|county','standard','checked'
#     fieldnames=[]
# 
#     # Set the first field to be the string of concatenated field names.
#     fieldnames.append(keyfields.replace(' ',''))
#     firstfield = True
# 
#     # Then add the remaining standard vocab fields.
#     for f in vocabfieldlist:
#         # in the case of composite key vocabualaries, do not use the first vocab
#         # field 'verbatim'. It is being replaced with the keyfields string.
#         if firstfield==True:
#             firstfield = False
#         else:
#             fieldnames.append(f)
#     return fieldnames
# 
# def writevocabheader(fullpath, fieldnames, dialect):
#     with open(fullpath, 'w') as csvfile:
#         writer = csv.DictWriter(csvfile, dialect=dialect, 
#             quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
#         writer.writeheader()
# 
# def readvocabheader(fullpath, dialect):
#     header = None
#     with open(fullpath, 'rU') as csvfile:
#         reader = csv.DictReader(csvfile, dialect=dialect, 
#             quoting=csv.QUOTE_ALL, skipinitialspace=True)
#         header=reader.fieldnames
#     return header
# 
def vocab_composite_appender(inputs_as_json):
    """Given a set of distinct key values for a given term composite, append any not already 
    in the corresponding vocabulary file as new entries.
    inputs_as_json - {'fullpath':'[i]', 'newvaluelist':'[n]', 'keyfields':'[k]'} where:
    i is the full path to the vocabulary input file
    n is a list of candidate key values to append
    k is a key made from a string of field names separated by '|'
    
    returns JSON string with information about the results."""

    global newvaluelist
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']
    keyfields = inputs['keyfields']
    logging.debug('inputs: %s \nfullpath: %s \nkeyfields: %s' 
        % (inputs, fullpath, keyfields))

    # Use the newvaluelist from the input JSON, if it exists. 
    # If it comes from inputs[], it should be a list. If it comes from the global 
    # variable, it will be a string
    logging.debug('newvaluelist: %s' % newvaluelist)
    if newvaluelist is None:
        try:
            # thelist should be a list
            newvaluelist = inputs['newvaluelist']
            logging.debug('try newvaluelist: %s' % newvaluelist)
        except:
            logging.debug('No newvaluelist given.')
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
    fieldnames = makevocabheader(keyfields)
    isfile = os.path.isfile(fullpath)
    
    # File doesn't exist, create it with a header consisting of fieldnames
    if not isfile:
        writevocabheader(fullpath, fieldnames, dialect)
    
    filesize = os.stat(fullpath).st_size
    # File is empty, recreate is with a header consisting of fieldnames
    if filesize == 0:
        writevocabheader(fullpath, fieldnames, dialect)

    # Now we should have a vocab file with a header at least
#    header = readvocabheader(fullpath, dialect)
    header = read_header(fullpath, dialect)
    logging.debug('fieldnames: %s \nheader: %s' % (fieldnames, header))

    # The header for the values we are trying to add has to match the header for the 
    # vocabulary file. If not, the vocabulary structure will be compromised.
    if fieldnames != header:
        logging.error('Input header:\n%s\nnot the same as the vocabulary file header:\n%s\nUnable to append new vocabulary values to %s' 
            % (fieldnames, header, fullpath) )
        return None
        
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

    logging.debug('Appender response: %s' % response)
    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to store vocabs",
                      default=None)
    parser.add_option("-k", "--keyfieldlist", dest="keyfieldlist",
                      help="Ordered list of fields that make up the key",
                      default=None)
    parser.add_option("-n", "--newvaluelist", dest="newvaluelist",
                      help="List of new values to add to the vocab",
                      default=None)
    parser.add_option("-s", "--separator", dest="separator",
                      help="The Separator that divides the values in the list",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="The level at which to log",
                      default='INFO')
    return parser.parse_args()[0]

def main():
    """
    Example: 
    python vocab_composite_appender.py -i ../../vocabularies/dwcgeography.csv -s , -k "continent|country |countrycode| stateprovince|county|municipality|waterbody|islandgroup|island " -n "|United States|California|||||, North America|United States|Washington|Chelan||||"
    """
    options = _getoptions()
    loglevel = options.loglevel
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
    fullpath = options.inputfile
    thelist=options.newvaluelist
    keyfields=options.keyfieldlist
    # Default separator is ','
    # For the purpose of demonstration, allow the command line to pass a 
    # user-defined-delimiter-separated list of values to add to the vocabulary. 
    separator = '\t' # TAB character
    if options.separator is not None:
        separator = options.separator
    newvaluelist=[subs.strip() for subs in str(thelist).split(separator)]
    logging.debug('newvaluelist: %s' % newvaluelist)

    if fullpath is None or thelist is None or keyfields is None:
        i = '../../vocabularies/dwcgeography.csv'
        s = '\t'
        k = '"continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island"'
        n = '"Oceania|United States|US|Hawaii|Honolulu|Honolulu|North Pacific Ocean|Hawaiian Islands|Oahu, |United States||WA|Chelan Co.||||"'
        l = "DEBUG"
        print "syntax: python vocab_composite_appender.py -i %s -s %s -l %s -k %s -n %s" % (i, s, l, k, n)
        return

    inputs = {}
    inputs['fullpath'] = fullpath
    inputs['newvaluelist'] = newvaluelist
    inputs['keyfields'] = keyfields
    logging.debug('inputs: %s' % inputs)
    logging.debug('json.dumps(inputs): %s' % json.dumps(inputs))

    # Append distinct values of to vocab file
    appendresult=vocab_composite_appender(json.dumps(inputs))
    if appendresult is None:
        logging.error('Header %s not consistent with header of file %s' % (keyfields, fullpath))
        return 0    
    response=json.loads(appendresult)
    logging.info('To file %s, added new values: %s' % (fullpath, response['addedvalues']))

if __name__ == '__main__':
    main()
