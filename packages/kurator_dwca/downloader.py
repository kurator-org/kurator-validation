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
__version__ = "downloader.py 2016-05-05T16:09-03:00"

from optparse import OptionParser
from dwca_utils import response
import logging
import uuid

# Uses the HTTP requests package
#   pip install requests
# Uses the unicodecsv package in dwca_utils
#   pip install unicodecsv
#
# For workflows
#   jython pip install requests
#   jython pip install unicodecsv
import requests

def downloader(options):
    """Download a file from a URL.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        outputfile - name of the output file, without path (optional)
        url - URL to the file to download (required)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the results
    """
#    print 'Started %s' % __version__
#    print 'options: %s' % options

    # Set up logging
    try:
        loglevel = options['loglevel']
    except:
        loglevel = None
    if loglevel is not None:
        if loglevel.upper() == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        elif loglevel.upper() == 'INFO':        
            logging.basicConfig(level=logging.INFO)

    logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    success = False
    message = None

    # inputs
    try:
        workspace = options['workspace']
    except:
        workspace = None

    if workspace is None:
        workspace = './'

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None:
        outputfile='dwca_'+str(uuid.uuid1())+'.zip'

    try:
        url = options['url']
    except:
        url = None

#    print 'options: %s' % options
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    success = download_file(url, outputfile)
    if success==True:
        artifacts['downloaded_file'] = outputfile

    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.info('Finishing %s' % __version__)
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
                      help="URL for the file to download (required)",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Output file name, no path (optional)",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file (optional)",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(e.g., DEBUG, WARNING, INFO) (optional)",
                      default=None)
    return parser.parse_args()[0]

def main():
    options = _getoptions()
    optdict = {}

    if options.url is None or len(options.url)==0:
        s =  'syntax: python downloader.py'
        s += ' -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals'
        s += ' -w ./workspace'
        s += ' -o test_ccber_mammals_dwc_archive.zip'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['url'] = options.url
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of to vocab file
    response=downloader(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    main()
