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
__version__ = "dwca_core_to_tsv.py 2016-04-21T13:49-03:00"

# Example: 
#
# kurator -f dwca_core_to_tsv.yaml \
#         -p dwcafile=../data/dwca-uwymv_herp.zip \
#         -p tsvfile=dwcatsvout.txt \
#         -p workspace=../workspace/ \
#         -p archivetype=standard
#
# or as a command-line script.
# Example:
#
# python dwca_core_to_tsv.py 
#        -i ./data/dwca-uwymv_herp.zip 
#        -o dwcatsvout.txt 
#        -w ./workspace/
#        -t standard

from optparse import OptionParser
from dwcareader_utils import short_term_names
from dwca_utils import tsv_dialect
from dwca_utils import response
import json
import csv
import uuid
import os.path
import logging

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
# jython pip install python-dwca-reader for use in workflows
from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader

def dwca_core_to_tsv(options):
    """Save the core of the archive to a tsv file with short DwC term names as headers.
    options - a dictionary of parameters
        workspace - path to a directory for the tsvfile (optional)
        dwcafile - full path to the input Darwin Core archive file (required)
        tsvfile - file name of the tsv output file, no path (optional)
        archivetype - the archive type ('standard' or 'gbif') (optional)
        loglevel - the level at which to log (e.g., DEBUG)
    returns JSON string with information about the results
        workspace - actual path to the directory where the outputfile was written
        tsvfile - actual full path to the output tsv file
        rowcount - the number of rows in the Darwin Core archive file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    print 'Started %s' % __version__
    print 'options: %s' % options

    # Set up logging
#     try:
#         loglevel = options['loglevel']
#     except:
#         loglevel = None
#     if loglevel is not None:
#         if loglevel.upper() == 'DEBUG':
#             logging.basicConfig(level=logging.DEBUG)
#         elif loglevel.upper() == 'INFO':        
#             logging.basicConfig(level=logging.INFO)
# 
#     logging.info('Starting %s' % __version__)

    # Make a list for the response
    returnvars = ['workspace', 'tsvfile', 'rowcount', 'success', 'message']

    # outputs
    tsvfile = None
    rowcount = None
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
        dwcafile = options['dwcafile']
    except:
        dwcafile = None

    if dwcafile is None or len(dwcafile)==0:
        message = 'No input dwca file given'
        returnvals = [workspace, tsvfile, rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(dwcafile) == False:
        message = 'Input dwca file not found'
        returnvals = [workspace, tsvfile, rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        tsvfile = options['tsvfile']
    except:
        tsvfile = None
    if tsvfile is None:
        tsvfile = '%s/dwca_%s.tsv' % (workspace.rstrip('/'), str(uuid.uuid1()))

    try:
        type = options['archivetype']
    except:
        type = 'standard'

    # Note: The DwCAReader creates a temporary directory of its own and cleans it up
    # Make a reader based on whether the archive is standard or a GBIF download.
    dwcareader = None
    if type=='gbif':
        try:
            dwcareader = GBIFResultsReader(dwcafile)
        except Exception, e:
            message = 'Error %s reading GBIF archive: %s' % (dwcafile, e)
            returnvals = [workspace, tsvfile, rowcount, success, message]
#            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)
    try:
        dwcareader = DwCAReader(dwcafile)
    except Exception, e:
        message = 'Error %s reading archive: %s' % (dwcafile, e)
        returnvals = [workspace, tsvfile, rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if dwcareader is None:
        message = 'No viable archive found at %s' % dwcafile
        returnvals = [workspace, tsvfile, rowcount, success, message]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)
    dialect = tsv_dialect()
    with open(tsvfile, 'w') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=shorttermnames)
        writer.writeheader()

    rowcount = 0
    with open(tsvfile, 'a') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=termnames)
        for row in dwcareader:
            for f in row.data:
                row.data[f]=row.data[f].encode("utf-8")
            writer.writerow(row.data)
            rowcount += 1

    # Close the archive    
    dwcareader.close()

    success = True
    returnvals = [workspace, tsvfile, rowcount, success, message]
    print 'returnvals: %s' % returnvals
#    logging.info('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      help="DwC archive to split",
                      default=None)
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      help="Path for output file",
                      default=None)
    parser.add_option("-w", "--workspace", dest="workspace",
                      help="Directory for the output file",
                      default=None)
    parser.add_option("-t", "--type", dest="type",
                      help="Type of Darwin Core archive ('gbif', 'standard')",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="(DEBUG, INFO)",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    optdict = {}

    dwcafile = options.inputfile
    tsvfile = options.outputfile
    archivetype = options.type

    if dwcafile is None or len(dwcafile)==0:
        s =  'syntax: python dwca_core_to_tsv.py'
        s += ' -i ../../data/dwca-uwymv_herp.zip'
        s += ' -w ./workspace'
        s += ' -o testout.txt -t standard'
        s += ' -l DEBUG'
        print '%s' % s
        return

    if archivetype is None:
        archivetype = 'standard'

    optdict['dwcafile'] = dwcafile
    optdict['workspace'] = options.workspace
    optdict['tsvfile'] = tsvfile
    optdict['archivetype'] = archivetype
    optdict['loglevel'] = options.loglevel

    # Write the core to a tsv file at the specified location
    response = dwca_core_to_tsv(optdict)
    print 'response: %s' % response
#    print 'TSV file %s with %s rows extracted from core of archive %s (type %s).' \
#        % (response['tsvfile'], response['rowcount'], dwcafile, archivetype)

if __name__ == '__main__':
    """ Demo of dwca_core_splitter"""
    main()
