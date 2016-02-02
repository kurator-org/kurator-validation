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
__version__ = "vocabs_appender.py 2016-02-01T18:06-03:00"

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/vocabs_appender.yaml -p p=fullpath -p v=../../data/eight_specimen_records.csv -p a=../../data/vocabularies -p t='basisOfRecord, sex'
#
# or as a command-line script.
# Example:
#
# python vocabs_appender.py -i ../../data/eight_specimen_records.csv -v ../../data/vocabularies -t 'basisOfRecord, sex'

from optparse import OptionParser
from vocab_extractor import vocab_extractor
from vocab_appender import vocab_appender
from dwca_terms import controlledtermlist as dwc_controlledtermlist
import json
import logging

# Global variable for the path to the directory in which to find the vocab files
vocabs_path = None

# Global variable for the list of terms for which to find distinct values
termlist = None

def vocabs_appender(inputs_as_json):
    """For all term names in a list set, find and append distinct values to the 
    appropriate vocabulary file.
    inputs_as_json - {'fullpath':'[p]', 'vocabs_path':'[v]'} where:
    p is the full path to the file from which to extract
    v is the path to the directory in which to find the vocab files
    
    returns JSON string with information about the results."""

    global vocabs_path
    global termlist
    inputs = json.loads(inputs_as_json)
    fullpath = inputs['fullpath']
    # Use the global termlist value, if it exists
    if termlist is None:
        try:
            thelist = inputs['termlist']
            termlist=[subs.strip() for subs in thelist.split(',')]
        except:
            termlist = dwc_controlledtermlist
    else:
        thelist = termlist
        termlist=[subs.strip() for subs in thelist.split(',')]
    # Use the vocabs_path from the input JSON, if it exists
    try:
        vocabs_path = inputs['vocabs_path']
    except:
        # Otherwise use the global value, if it exists
        if vocabs_path is None:
            print 'No vocabs_path given.'
            return None

    print 'fullpath: %s vocabs_path: %s termlist: %s' % (fullpath, vocabs_path, termlist)
    terms_updated = []
    logging.debug('termlist: %s' % termlist)
    for t in termlist:
        vocab_file = '%s/%s.csv' % (vocabs_path, t)
        extractor_params = {}
        extractor_params['fullpath'] = fullpath
        extractor_params['termname'] = t
        extractor_response = vocab_extractor(json.dumps(extractor_params))
        print 'vocab_extractor response: %s' % extractor_response
        logging.debug('vocab_extractor response: %s' % extractor_response)
 
        if extractor_response is not None:
            response=json.loads(extractor_response)
            vocab = response['valueset']
            appender_params = {}
            appender_params['fullpath'] = vocab_file
            appender_params['newvaluelist'] = vocab
            print 'appender_params: %s' % appender_params
            appender_response = vocab_appender(json.dumps(appender_params))
            print 'vocab_appender response: %s' % appender_response
            logging.debug('vocab_appender response: %s' % appender_response)

            if appender_response is not None:
                response=json.loads(appender_response)
                addedterms=response['addedvalues']
                if len(addedterms)>0:
                    terms_updated.append(t)
        
    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['terms_updated']
    returnvals = [terms_updated]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1

    # Reset global variables to None
    vocabs_path = None
    termlist = None

    print 'Vocabs appender response: %s' % response['terms_updated']
    return json.dumps(response)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="Text file to store vocabs",
                      default=None)
    parser.add_option("-v", "--vocabs_path", dest="vocabs_path",
                      help="The path to the vocab files",
                      default=None)
    parser.add_option("-t", "--termlist", dest="termlist",
                      help="A list of terms to extract values from",
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
    local_vocabs_path = options.vocabs_path
    termlist=options.termlist
    
    if fullpath is None or local_vocabs_path is None:
        print "syntax: python vocabs_appender.py -i ../../data/eight_specimen_records.csv -v ../../data/vocabularies -t 'basisOfRecord, sex'"
        return
    
    inputs = {}
    inputs['fullpath'] = fullpath
    inputs['termlist'] = termlist
    inputs['vocabs_path'] = local_vocabs_path
    
    # Append distinct values of to vocab file
    response=json.loads(vocabs_appender(json.dumps(inputs)))

    logging.info('File %s had new values saved in %s for: %s' %
        (fullpath, local_vocabs_path, response['terms_updated']) )

if __name__ == '__main__':
    """ Demo of vocabs_appender"""
    main()
