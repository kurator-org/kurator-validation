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
__version__ = "downloader.py 2016-02-22T17:30-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/downloader.yaml -p u=http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals -p o=test_ccber_archive.zip
#
# or as a command-line script.
# Example:
#
# python downloader.py -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals -o test_ccber_archive.zip

from optparse import OptionParser
from dwcareader_utils import download_file
from dwca_utils import response
import json
import logging

def downloader(inputs_as_json):
    """Download a file from a URL.
    inputs_as_json - JSON string containing inputs
        url - full path to the file to download
        outputfile - full path to the output file
    returns JSON string with information about the results
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['success', 'message']

    # outputs
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        url = inputs['url']
    except:
        url = None
    try:
        outputfile = inputs['outputfile']
    except:
        outputfile = None

    if outputfile is None:
        message = 'No output file given'
        returnvals = [success, message]
        return response(returnvars, returnvals)

    success = download_file(url, outputfile)
    returnvals = [success, message]
    return response(returnvars, returnvals)
    
def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      help="Url for the file to download",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Output file",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    url = options.url
    outputfile = options.outputfile

    if url is None or outputfile is None:
        print "syntax: python downloader.py -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals -o test_ccber_archive.zip"
        return
    
    inputs = {}
    inputs['url'] = url
    inputs['outputfile'] = outputfile

    # Append distinct values of to vocab file
    response=json.loads(downloader(json.dumps(inputs)))
#    print 'response: %s' % response
    logging.debug('To file %s, added new values: %s' % (url, response['success']))

if __name__ == '__main__':
    main()
