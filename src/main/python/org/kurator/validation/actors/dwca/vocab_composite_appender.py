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
__version__ = "vocab_composite_appender.py 2016-02-19T22:33-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
# TODO: Update this
# kurator -f workflows/vocab_composite_appender.yaml -p i=../../vocabularies/dwcgeography.txt -p s='\t' -p k="continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island" -p n="|United States|California|||||, North America|United States|Washington|Chelan||||"
#
# or as a command-line script.
# Example:
#
# python vocab_composite_appender.py -i ../../vocabularies/dwcgeography.txt -s , -k "continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island" -n "|United States|California|||||, North America|United States|Washington|Chelan||||"

from optparse import OptionParser
from dwca_utils import read_header
from vocab_extractor import vocab_extractor
from dwca_vocab_utils import makevocabheader
from dwca_vocab_utils import writevocabheader
from dwca_vocab_utils import vocab_dialect
from dwca_vocab_utils import distinct_term_values_from_file
from dwca_vocab_utils import not_in_list
from dwca_terms import vocabfieldlist
import os.path
import csv
import json

# Global variable for the list of potentially new values for the term to append to the vocab file
newvaluelist = None

def vocab_composite_appender(inputs_as_json):
    """Given a set of distinct key values for a given term composite (a combination of 
    terms), append any not already in the corresponding vocabulary file as new entries.
    inputs_as_json - JSON string containing inputs
        vocabfile - full path to the file containing the vocabulary
        newvaluelist - a list of candidate key values to append
        keyfields - a key made from a string of field names
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        addedvalues - new composite key values added to the vocabulary file
    """
    global newvaluelist
    inputs = json.loads(inputs_as_json)
    vocabfile = inputs['vocabfile']
    keyfields = inputs['keyfields']

    # Use the newvaluelist from the input JSON, if it exists. 
    # If it comes from inputs[], it should be a list. If it comes from the global 
    # variable, it will be a string
    if newvaluelist is None:
        try:
            # thelist should be a list
            newvaluelist = inputs['newvaluelist']
        except:
            return None
    else:
        # newvaluelist should be a string
        thelist = newvaluelist
        if str(newvaluelist).find(',')>0:
            newvaluelist=[subs.strip() for subs in thelist.split(',')]
        else:
            newvaluelist=[str(newvaluelist)]

    dialect = vocab_dialect()
    fieldnames = makevocabheader(keyfields)
#    print 'keyfields:\n%sfieldnames:\n%s' % (keyfields, fieldnames)
    isfile = os.path.isfile(vocabfile)
    
    # If file doesn't exist, create it with a header consisting of fieldnames
    if not isfile:
        writevocabheader(vocabfile, fieldnames, dialect)
    
    filesize = os.stat(vocabfile).st_size
    # If file is empty, recreate is with a header consisting of fieldnames
    if filesize == 0:
        writevocabheader(vocabfile, fieldnames, dialect)

    # Now we should have a vocab file with a header at least
    header = read_header(vocabfile, dialect)

    # The header for the values we are trying to add has to match the header for the 
    # vocabulary file. If not, the vocabulary structure will be compromised.
    if fieldnames != header:
        return None
    if keyfields != header[0]:
        return None

    existingvalues = distinct_term_values_from_file(vocabfile, keyfields)        
    addedvalues = not_in_list(existingvalues, newvaluelist)
#     print 'existingvalues:\n%s' % existingvalues
#     print 'newvaluelist:\n%s' % newvaluelist
#     print 'addedvalues:\n%s' % addedvalues
    with open(vocabfile, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, dialect=dialect, fieldnames=vocabfieldlist)
        for term in addedvalues:
            if term!='':
                writer.writerow({'verbatim':term, 'standard':'', 'checked':0 })

    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['addedvalues', 'success']
    returnvals = [addedvalues, True]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    newvaluelist = None

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
    return parser.parse_args()[0]

def main():
    """
    Example: 
    python vocab_composite_appender.py -i ../../vocabularies/dwcgeography.txt -s , -k "continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island" -n "|United States|California|||||, North America|United States|Washington|Chelan||||"
    """
    options = _getoptions()
    vocabfile = options.inputfile
    thelist=options.newvaluelist
    keyfields=options.keyfieldlist
    # Default separator is '\t'
    # For the purpose of demonstration, allow the command line to pass a 
    # user-defined-delimiter-separated list of values to add to the vocabulary. 
    separator = '\t' # TAB character
    if options.separator is not None:
        separator = options.separator
    newvaluelist=[subs.strip() for subs in str(thelist).split(separator)]

    if vocabfile is None or thelist is None or keyfields is None:
        i = '../../vocabularies/dwcgeography.csv'
        s = '\t'
        k = '"continent|country|countrycode|stateprovince|county|municipality|waterbody|islandgroup|island"'
        n = '"Oceania|United States|US|Hawaii|Honolulu|Honolulu|North Pacific Ocean|Hawaiian Islands|Oahu, |United States||WA|Chelan Co.||||"'
        print "syntax: python vocab_composite_appender.py -i %s -s %s -k %s -n %s" % (i, s, k, n)
        return

    inputs = {}
    inputs['vocabfile'] = vocabfile
    inputs['newvaluelist'] = newvaluelist
    inputs['keyfields'] = keyfields

    # Append distinct values of to vocab file
    appendresult=vocab_composite_appender(json.dumps(inputs))
    if appendresult is None:
        return 0    
    response=json.loads(appendresult)

if __name__ == '__main__':
    main()
