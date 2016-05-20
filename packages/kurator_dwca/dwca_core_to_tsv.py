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
__version__ = "dwca_core_to_tsv.py 2016-05-11T16:04-03:00"

from optparse import OptionParser
from dwcareader_utils import short_term_names
from dwca_utils import tsv_dialect
from dwca_utils import response
import csv
import uuid
import os
import logging

# Python Darwin Core Archive Reader from 
#   https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
#   pip install python-dwca-reader
#   jython pip install python-dwca-reader for use in workflows
from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader

def dwca_core_to_tsv(options):
    """Save the core of the archive to a tsv file with short DwC term names as headers.
    options - a dictionary of parameters
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input Darwin Core archive file (required)
        outputfile - file name of the tsv output file, no path (optional)
        archivetype - the archive type ('standard' or 'gbif') (optional)
        loglevel - the level at which to log (e.g., DEBUG)
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        rowcount - the number of rows in the Darwin Core archive file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    """
    logging.info( 'Started %s' % __version__ )
    logging.info( 'options: %s' % options )

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
    returnvars = ['workspace', 'outputfile', 'rowcount', 'success', 'message', 
        'artifacts']

    # Make a dictionary for artifacts left behind
    artifacts = {}

    # outputs
    outputfile = None
    rowcount = None
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
        inputfile = options['inputfile']
    except:
        inputfile = None

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given'
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file not found'
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        outputfile = None

    if outputfile is None or len(outputfile)==0:
        outputfile = 'dwca_%s.tsv' %  str(uuid.uuid1())
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    try:
        type = options['archivetype']
    except:
        type = 'standard'

    # Note: The DwCAReader creates a temporary directory of its own and cleans it up
    # Make a reader based on whether the archive is standard or a GBIF download.
    dwcareader = None
    if type=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            message = 'Error %s reading GBIF archive: %s' % (inputfile, e)
            returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)
    try:
        dwcareader = DwCAReader(inputfile)
    except Exception, e:
        message = 'Error %s reading archive: %s' % (inputfile, e)
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if dwcareader is None:
        message = 'No viable archive found at %s' % inputfile
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)
    dialect = tsv_dialect()
    with open(outputfile, 'w') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=shorttermnames)
        writer.writeheader()

    rowcount = 0
    with open(outputfile, 'a') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=termnames)
        for row in dwcareader:
            for f in row.data:
                row.data[f]=row.data[f].encode("utf-8")
            writer.writerow(row.data)
            rowcount += 1

    # Close the archive    
    dwcareader.close()

    success = True
    if success==True:
        artifacts['outputfile'] = outputfile

    returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
#    logging.debug('message:\n%s' % message)
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
    options = _getoptions()
    optdict = {}

    inputfile = options.inputfile
    outputfile = options.outputfile
    archivetype = options.type

    if inputfile is None or len(inputfile)==0:
        s =  'syntax: python dwca_core_to_tsv.py'
        s += ' -i ./data/dwca-uwymv_herp.zip'
        s += ' -w ./workspace'
        s += ' -o testout.txt -t standard'
        s += ' -l DEBUG'
        print '%s' % s
        return

    if archivetype is None:
        archivetype = 'standard'

    optdict['inputfile'] = inputfile
    optdict['workspace'] = options.workspace
    optdict['outputfile'] = outputfile
    optdict['archivetype'] = archivetype
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Write the core to a tsv file at the specified location
    response = dwca_core_to_tsv(optdict)
    print 'response: %s' % response

if __name__ == '__main__':
    """ Demo of dwca_core_splitter"""
    main()
