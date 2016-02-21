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
__version__ = "dwca_core_to_tsv.py 2016-02-21T17:51-03:00"

# TODO: Integrate pattern for calling actor in a workflow using dictionary of parameters
# OBSOLETE: Use global variables for parameters sent at the command line in a workflow
#
# Example: 
#
# kurator -f workflows/dwca_core_to_tsv.yaml -p dwcafile=../../data/dwca-uwymv_herp.zip -p tsvoutputfile=./workspace/dwcatsvout.txt -p archivetype=standard
#
# or as a command-line script.
# Example:
#
# python dwca_core_to_tsv.py -i ../../data/dwca-uwymv_herp.zip -o ./workspace/dwcatsvout.txt -t standard

from optparse import OptionParser
from dwcareader_utils import short_term_names
from dwca_utils import tsv_dialect
from dwca_utils import response
import json
import csv
import os.path
import logging

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
# jython pip install python-dwca-reader for use in workflows
from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader

def dwca_core_to_tsv(inputs_as_json):
    """Save the core of the archive to a tsv file with short DwC term names as headers.
    inputs_as_json - JSON string containing inputs
        dwcafile - full path to the input Darwin Core archive file
        tsvfile - Full path to the tsv output file
        archivetype - the archive type ('standard' or 'gbif')
    returns JSON string with information about the results
        rowcount - the number of rows in the Darwin Core archive file
        success - True if process completed successfully, otherwise False
        message - an explanation of the reason if success=False
    """
    # Make a list for the response
    returnvars = ['rowcount', 'success', 'message']

    # outputs
    rowcount = None
    success = False
    message = None

    # inputs
    inputs = json.loads(inputs_as_json)
    try:
        inputfile = inputs['dwcafile']
    except:
        inputfile = None
    try:
        tsvfilename = inputs['tsvfile']
    except:
        tsvfilename = None
    try:
        type = inputs['archivetype']
    except:
        type = 'standard'

    if inputfile is None:
        message = 'No input file given'
        returnvals = [rowcount, success, message]
        return response(returnvars, returnvals)
        
    if tsvfilename is None:
        message = 'No output file given'
        returnvals = [rowcount, success, message]
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'input file not found'
        returnvals = [rowcount, success, message]
        return response(returnvars, returnvals)

    # Make a reader based on whether the archive is standard or a GBIF download.
    dwcareader = None
    if type=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            message = 'Error %s reading GBIF archive: %s' % (inputfile, e)
            returnvals = [rowcount, success, message]
            return response(returnvars, returnvals)
    try:
        dwcareader = DwCAReader(inputfile)
    except Exception, e:
        message = 'Error %s reading archive: %s' % (inputfile, e)
        returnvals = [rowcount, success, message]
        return response(returnvars, returnvals)

    if dwcareader is None:
        message = 'No viable archive found at %s' % inputfile
        returnvals = [rowcount, success, message]
        return response(returnvars, returnvals)

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)
    dialect = tsv_dialect()
    with open(tsvfilename, 'w') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=shorttermnames)
        writer.writeheader()

    rowcount = 0
    with open(tsvfilename, 'a') as thefile:
        writer = csv.DictWriter(thefile, dialect=dialect, fieldnames=termnames)
        for row in dwcareader:
            for f in row.data:
                row.data[f]=row.data[f].encode("utf-8")
            writer.writerow(row.data)
            rowcount += 1

    # Close the archive    
    dwcareader.close()
    success = True
    
    returnvals = [rowcount, success, message]
    return response(returnvars, returnvals)

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputfile",
                      help="DwC archive to split",
                      default=None)
    parser.add_option("-o", "--output", dest="outputfile",
                      help="Path for output file",
                      default=None)
    parser.add_option("-t", "--type", dest="type",
                      help="Type of Darwin Core archive ('gbif', 'standard')",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    dwcafile = options.inputfile
    tsvfile = options.outputfile
    archivetype = options.type

    if dwcafile is None:
        print 'syntax: python dwca_core_to_tsv.py -i ../../data/dwca-uwymv_herp.zip -o testout.txt -t standard'
        return

    if tsvfile is None:
        tsvfile = './dwcatotsv.txt'

    if archivetype is None:
        archivetype = 'standard'

    inputs = {}
    inputs['dwcafile'] = dwcafile
    inputs['tsvfile'] = tsvfile
    inputs['archivetype'] = archivetype

    # Write the core to a tsv file at the specified location
    response = json.loads(dwca_core_to_tsv(json.dumps(inputs)))
    
    print 'TSV file %s with %s rows extracted from core of archive %s (type %s).' \
        % (response['tsvfile'], response['rowcount'], dwcafile, archivetype)
    print 'Response: %s' % response

if __name__ == '__main__':
    """ Demo of dwca_core_splitter"""
    main()
