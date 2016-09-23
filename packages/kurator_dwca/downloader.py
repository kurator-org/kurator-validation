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
__version__ = "downloader.py 2016-09-23T121:00+02:00"

from dwca_utils import response
from dwca_utils import setup_actor_logging
import logging
import uuid
import argparse

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
        artifacts - a dictionary of persistent objects created
    """
    # print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

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

    if workspace is None or len(workspace)==0:
        workspace = './'

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None
    if outputfile is None or len(outputfile)==0:
        outputfile='dwca_'+str(uuid.uuid1())+'.zip'

    try:
        url = options['url']
    except:
        url = None

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    success = download_file(url, outputfile)
    if success==True:
        artifacts['downloaded_file'] = outputfile

    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
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
        logging.info('No URL given in download_file()')
        return False

    if outputfile is None or len(outputfile)==0:
        logging.info('No output file given in download_file()')
        return False

    try:
        # Note that calls to https destinations will log an InsecureRequestWarning. To 
        # avoid these warnings, enable certificate verification on the operating system 
        # and remove the verify=False parameter in the requests.get() call.
        r = requests.get(url, stream=True, verify=False)
    except Exception, e:
        s = 'Exception while attempting requests.get(url) in download_file(): %s' % e
        logging.warning(s)
        return False
    if not r.ok:
        s = 'Return value of requests.get(url) not ok in download_file(): %s' % r
        logging.warning(s)
        return False

    # Example outputfile: './workspace/test_ccber_mammals_dwc_archive.zip'
    with open(outputfile, 'wb') as handle:
        for block in r.iter_content(1024):
            handle.write(block)

    return True

def _getoptions():
    """Parse command line options and return them."""
    parser = argparse.ArgumentParser()

    help = 'URL of the file to download (required)'
    parser.add_argument("-u", "--url", help=help)

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    if options.url is None or len(options.url)==0:
        s =  'syntax:\n'
        s += 'python downloader.py'
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
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
