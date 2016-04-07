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
__version__ = "downloader.py 2016-04-06T19:14-03:00"

# Example: 
#
# kurator -f downloader.yaml \
#         -p u=http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals 
#         -p o=../workspace/test_ccber_mammals_dwc_archive.zip
#
# or as a command-line script.
# Example:
#
# python downloader.py \
#         -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals 
#         -o ./workspace/test_ccber_mammals_dwc_archive.zip

from optparse import OptionParser
from dwca_utils import response

# Uses the HTTP requests package
# pip install requests
# jython pip install requests for use in workflows
import requests

def downloader(options):
    """Download a file from a URL.
    options - a dictionary of parameters
        url - full path to the file to download
        outputfile - full path to the output file
    returns a dictionary with information about the results
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['success', 'message']

    # outputs
    success = False
    message = None

    # inputs
    try:
        url = options['url']
    except:
        url = None
    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        message = 'No output file given'
        returnvals = [success, message]
        return response(returnvars, returnvals)

    success = download_file(url, outputfile)
    returnvals = [success, message]
    return response(returnvars, returnvals)

def download_file(url, outputfile):
    """Get a file from a URL.
    parameters:
        url - the url to download from
            (e.g., 'http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals')
        outputfile - the full path to the location for the output file
    returns:
        success - True if the file was downloaded, False if the request was unsuccessful
    """
    if url is None or len(url)==0:
        return False
    if outputfile is None or len(outputfile)==0:
        return False

    try:
        r = requests.get(url, stream=True)
    except:
        return False
    if not r.ok:
        return False

    # Example outputfile: './workspace/test_ccber_mammals_dwc_archive.zip'
    with open(outputfile, 'wb') as handle:
        for block in r.iter_content(1024):
            handle.write(block)
    return True

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      help="URL for the file to download",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Full path to the output file",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.url is None or len(options.url)==0 or \
        options.outputfile is None or len(options.outputfile)==0:
        s =  'syntax: python downloader.py'
        s += ' -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals'
        s += ' -o ./workspace/test_ccber_mammals_dwc_archive.zip'
        print '%s' % s
        return

    optdict['url'] = options.url
    optdict['outputfile'] = options.outputfile

    # Append distinct values of to vocab file
    response=downloader(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
