#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "downloader.py 2017-04-27T16:37-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import response
from dwca_utils import setup_actor_logging
import logging
import uuid
import argparse
try:
    from urllib.request import urlretrieve  # Python 3
except ImportError:
    from urllib import urlretrieve  # Python 2

def downloader(options):
    ''' Download a files from a list of URLs.
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        url - URL to the file to download (required)
        outputfile - name of the output file, without path (optional)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output file
        success - True if process completed successfully, otherwise False
        message - an explanation of the results
        artifacts - a dictionary of persistent objects created
    '''
    #print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    url = None
    outputfile = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        url = options['url']
    except:
        pass

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        outputfile='dwca_'+str(uuid.uuid1())+'.zip'

    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    success = download_file(url, outputfile)

    if success==True:
        artifacts['downloaded_file'] = outputfile

    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def download_file(url, outputfile):
    ''' Get a file from a URL.
    parameters:
        url - the url to download from
            (e.g., 'http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals')
        outputfile - the full path to the location for the output file
    returns:
        success - True if the file was downloaded, False if the request was unsuccessful
    '''
    functionname = 'download_file()'

    if url is None or len(url)==0:
        s = 'No URL given in %s' % functionname
        logging.info(s)
        return False

    if outputfile is None or len(outputfile)==0:
        s = 'No output file given in %s' % functionname
        logging.info(s)
        return False

    try:
        urlretrieve(url, outputfile)
    except Exception, e:
        s = 'Exception while attempting urlretrieve(%s, %s):\n%s\n' % (url, outputfile, e)
        s += '%s' % functionname
        logging.warning(s)
        return False

    return True

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'URL of the file to download (required)'
    parser.add_argument("-u", "--url", help=help)

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
        s += ' -w ./workspace'
        s += ' -u http://ipt.vertnet.org:8080/ipt/archive.do?r=ccber_mammals'
        s += ' -o test_ccber_mammals_dwc_archive.zip'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['url'] = options.url
    optdict['outputfile'] = options.outputfile
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Append distinct values of to vocab file
    response=downloader(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
