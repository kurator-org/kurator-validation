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
__copyright__ = "Copyright 2016 President and Fellows of Harvard College"
__version__ = "dwca_core_to_tsv.py 2016-10-04T16:26+02:00"

from dwcareader_utils import short_term_names
from dwca_utils import tsv_dialect
from dwca_utils import response
from dwca_utils import write_header
from dwca_utils import setup_actor_logging
import uuid
import os
import logging
import argparse

# Replace the system csv with unicodecsv. All invocations of csv will use unicodecsv,
# which supports reading and writing unicode streams.
try:
    import unicodecsv as csv
except ImportError:
    import warnings
    s = "The unicodecsv package is required.\n"
    s += "pip install unicodecsv\n"
    s += "$JYTHON_HOME/bin/pip install unicodecsv"
    warnings.warn(s)

# Requires the Python Darwin Core Archive Reader from 
#   https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
try:
    from dwca.read import DwCAReader
    from dwca.read import GBIFResultsReader
except ImportError:
    import warnings
    s = "The python-dwca-reader package is required.\n"
    s += "pip install python-dwca-reader\n"
    s += "$JYTHON_HOME/bin/pip install python-dwca-reader"
    warnings.warn(s)

def dwca_core_to_tsv(options):
    ''' Save the core of the archive to a tsv file with DwC term names as headers.
    options - a dictionary of parameters
        loglevel - the level at which to log (e.g., DEBUG)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input Darwin Core archive file (required)
        outputfile - file name of the tsv output file, no path (optional)
        archivetype - archive type ('standard' or 'gbif') (optional; default 'standard')
    returns a dictionary with information about the results
        workspace - actual path to the directory where the outputfile was written
        outputfile - actual full path to the output tsv file
        rowcount - the number of rows in the Darwin Core archive file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
        artifacts - a dictionary of persistent objects created
    '''
    print '%s options: %s' % (__version__, options)

    setup_actor_logging(options)

    logging.debug( 'Started %s' % __version__ )
    logging.debug( 'options: %s' % options )

    # Make a list for the response
    returnvars = ['workspace', 'outputfile', 'rowcount', 'success', 'message', 
        'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    rowcount = None

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    workspace = './'
    inputfile = None
    outputfile = None
    archivetype = 'standard'

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        pass

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    # Look to see if the input file is at the absolute path or in the workspace.
    if os.path.isfile(inputfile) == False:
        if os.path.isfile(workspace+'/'+inputfile) == True:
            inputfile = workspace+'/'+inputfile
        else:
            message = 'Input file %s not found. %s' % (inputfile, __version__)
            returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        outputfile = 'dwca_%s.txt' %  str(uuid.uuid1())
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    try:
        archivetype = options['archivetype']
    except:
        pass

    # Note: The DwCAReader creates a temporary directory of its own and cleans it up
    # Make a reader based on whether the archive is standard or a GBIF download.
    dwcareader = None
    if archivetype=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            message = 'Error %s ' % e
            message += 'reading GBIF archive: %s. %s' % (inputfile, __version__)
            returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
            logging.debug('message:\n%s' % message)
            return response(returnvars, returnvals)
    try:
        dwcareader = DwCAReader(inputfile)
    except Exception, e:
        message = 'Error %s reading archive %s. %s' % (e, inputfile, __version__)
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if dwcareader is None:
        message = 'No viable archive found at %s. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)
    dialect = tsv_dialect()

    success = write_header(outputfile, shorttermnames, dialect)
    if success == False:
        message = 'Unable to write header to %s. %s' % (outputfile, __version__)
        returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

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
        artifacts['dwca_core_to_tsv_outputfile'] = outputfile

    returnvals = [workspace, outputfile, rowcount, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'directory for the output file (optional)'
    parser.add_argument("-w", "--workspace", help=help)

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

    help = 'output file name, no path (optional)'
    parser.add_argument("-o", "--outputfile", help=help)

    help = "type of Darwin Core archive ('gbif', 'standard') (optional)"
    parser.add_argument("-t", "--archivetype", help=help)

    help = 'log level (e.g., DEBUG, WARNING, INFO) (optional)'
    parser.add_argument("-l", "--loglevel", help=help)

    return parser.parse_args()

def main():
    options = _getoptions()
    optdict = {}

    inputfile = options.inputfile
    outputfile = options.outputfile
    archivetype = options.type

    if inputfile is None or len(inputfile)==0:
        s =  'syntax:\n'
        s += 'python dwca_core_to_tsv.py'
        s += ' -w ./workspace'
        s += ' -i ./data/dwca-uwymv_herp.zip'
        s += ' -o testout.txt'
        s += ' -t standard'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['workspace'] = options.workspace
    optdict['inputfile'] = inputfile
    optdict['outputfile'] = outputfile
    optdict['archivetype'] = archivetype
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # Write the core to a tsv file at the specified location
    response = dwca_core_to_tsv(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    """ Demo of dwca_core_splitter"""
    main()
