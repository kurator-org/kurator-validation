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
__copyright__ = "Copyright 2015 President and Fellows of Harvard College"
__version__ = "dwca_core_to_tsv.py 2015-09-10T17:57:41s-07:00"

from optparse import OptionParser
from dwca_utils import short_term_names
from dwca_utils import get_core_rowcount
import json
import csv
import os.path
import logging
import text_file_splitter

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
# jython pip install python-dwca-reader for use in workflows
from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader

# For now, use global variables to capture parameters sent at the command line in 
# a workflow
# Example: 
#
# kurator -f workflows/dwca_core_to_tsv.yaml -p dwcafile=../../data/dwca-uwymv_herp.zip -p tsvoutputfile=./workspace/dwcatsvout.tsv -p archivetype=standard
#
# or as a command-line script.
# Example:
#
# python dwca_core_to_tsv.py -i ../../data/dwca-uwymv_herp.zip -o ./workspace/dwcatsvout.tsv -t standard  

dwcafile=None
tsvoutputfile='./dwcatsvout.tsv'
archivetype='standard'

def dwca_core_to_tsv():
    """Save the core of the archive to a csv file with short DwC term names as headers."""
    inputfile = dwcafile
    fullpath = tsvoutputfile

    if not os.path.isfile(inputfile):
        return None

    # Make an appropriate reader based on whether the archive is standard or a GBIF
    # download.
    dwcareader = None
    if type=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            logging.error('GBIF archive %s has an exception: %s ' % (inputfile, e))
            pass
    else:
        dwcareader = DwCAReader(inputfile)
    if dwcareader is None:
        print 'No viable archive found at %s' % inputfile
        return None

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)
    dialect = csv.excel
    dialect.lineterminator='\r'
    dialect.delimiter='\t'
    with open(fullpath, 'w') as tsvfile:
        writer = csv.DictWriter(tsvfile, dialect=dialect, fieldnames=shorttermnames, 
            quoting=csv.QUOTE_NONE, quotechar='')
        writer.writeheader()
 
    rowcount = 0
    with open(fullpath, 'a') as tsvfile:
        writer = csv.DictWriter(tsvfile, dialect=dialect, fieldnames=termnames,
            quoting=csv.QUOTE_NONE, quotechar='')
        for row in dwcareader:
#            print 'Row %s:\n%s' % (rowcount,row.data)
            for f in row.data:
                row.data[f]=row.data[f].encode("utf-8")
            writer.writerow(row.data)
            rowcount += 1

    # Get the number of records in the core file.
#    rowcount = get_core_rowcount(dwcareader)

    # Close the archive    
    dwcareader.close()
    
    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['fullpath', 'rowcount']
    returnvals = [fullpath, rowcount]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)

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
    global dwcafile, tsvoutputfile, archivetype
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    dwcafile = options.inputfile
    tsvoutputfile = options.outputfile
    archivetype = options.type
    if dwcafile is None:
        print 'syntax: python dwca_core_to_tsv.py -i ../../data/dwca-uwymv_herp.zip -o testout.tsv -t standard'
        return
    if tsvoutputfile is None:
        tsvoutputfile = 'dwca_core_to_tsv_output.tsv'
    if archivetype is None:
        type = 'standard'

    # Write the core to a tsv file at the specified location
    response = json.loads(dwca_core_to_tsv())
    
    print 'TSV file %s with %s rows extracted from core of archive %s (type %s).' \
        % (response['fullpath'], response['rowcount'], dwcafile, archivetype)
    print 'Response: %s' % response

if __name__ == '__main__':
    """ Demo of dwca_core_splitter"""
    main()
