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
__version__ = "dwca_core_extractor.py 2015-11-06T15:32:15+01:00"

from optparse import OptionParser
from dwca_utils import short_term_names
from dwcareader_utils import get_core_rowcount
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
# kurator -f workflows/dwca_core_extractor.yaml -p dwcafile=../../data/dwca-uwymv_herp.zip -p outputfile=./workspace/dwcatsvout.tsv -p archivetype=standard
#
# or as a command-line script.
# Example:
#
# python dwca_core_extractor.py -i ../../data/dwca-uwymv_herp.zip -o ./workspace/dwcatsvout.tsv -t standard  

dwcafile=None
outputfile=None
delimiter=None
quoting=None
archivetype=None
escapechar=None
quotechar=None

def dwca_core_extractor(inputs_as_json):
    """Save the core of the archive to a delimited file with short DwC term names as headers.
    inputs_as_json - {'dwcafile':'[i]', 'outputfile':'[o]', 'delimiter':'[d]', 'archivetype':'[t]'} 
    where:
    i - full path to the Darwin Core archive input file
    o - full path for the extracted output file
    d - field delimiter for the output file
    s - quoting style ('NONE', 'MINIMAL', 'ALL', NONNUMERIC')
    q - quote character
    e - escape character
    t - input Darwin Core archive type ('standard' or 'gbif')

    returns JSON string with information about the results."""

    global dwcafile, outputfile, delimiter, quoting, escapechar, quotechar, archivetype

    if dwcafile is None:
        try:
            dwcafile = inputs['dwcafile']
        except:
            logging.debug('No dwcafile given.')
            return None
    if not os.path.isfile(dwcafile):
        logging.debug('The file %s was not found.')
        return None

    if outputfile is None:
        try:
            outputfile = inputs['outputfile']
        except:
            logging.debug('No outputfile given.')
            return None

    if delimiter is None:
        try:
            delimiter = inputs['delimiter']
        except:
            logging.debug('No delimiter given.')
            delimiter=','

    if escapechar is None:
        try:
            escapechar = inputs['escapechar']
        except:
            logging.debug('No escape character given.')
            escapechar=''

    if quotechar is None:
        try:
            quotechar = inputs['quotechar']
        except:
            logging.debug('No quote character given.')
            quotechar=''

    if quoting is None:
        try:
            quoting = inputs['quoting']
            if quoting == 'ALL':
                quoting=csv.QUOTE_ALL
            elif quoting == 'MINIMAL':
                quoting = csv.QUOTE_MINIMAL
            elif quoting == 'NONNUMERIC':
                quoting = csv.QUOTE_NONNUMERIC
            else:
                quoting = csv.QUOTE_NONE
        except:
            logging.debug('No quoting style given.')
            quoting = csv.QUOTE_NONE

    if archivetype is None:
        try:
            archivetype = inputs['archivetype']
        except:
            logging.debug('No archivetype given.')
            archivetype='standard'

    # Make an appropriate reader based on whether the archive is standard or a GBIF
    # download.
    dwcareader = None
    if archivetype=='gbif':
        try:
            dwcareader = GBIFResultsReader(dwcafile)
        except Exception, e:
            logging.error('GBIF archive %s has an exception: %s ' % (dwcafile, e))
            pass
    else:
        dwcareader = DwCAReader(dwcafile)
    if dwcareader is None:
        print 'No viable archive found at %s' % dwcafile
        return None

    termnames=list(dwcareader.descriptor.core.terms)
    shorttermnames=short_term_names(termnames)

    dialect = csv.excel
    dialect.lineterminator='\r'
    dialect.delimiter=delimiter
    dialect.escapechar=escapechar

    with open(outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect=dialect, fieldnames=shorttermnames, 
            quoting=quoting, quotechar='"')
        writer.writeheader()
 
    rowcount = 0
    failedrowcount = 0
    with open(outputfile, 'a') as outfile:
        writer = csv.DictWriter(outfile, dialect=dialect, fieldnames=termnames,
            quoting=csv.QUOTE_NONE, quotechar=quotechar)
        for row in dwcareader:
#            logging.debug('Row %s:\n%s' % (rowcount,row.data) )
            rowcount += 1
            for f in row.data:
                row.data[f]=row.data[f].encode("utf-8")
            try:
                writer.writerow(row.data)
            except:
                failedrowcount += 1
#                    logging.warning('Row failed to write with chosen Writer settings:\n%s' % row.data)

    # Get the number of records in the core file.
#    rowcount = get_core_rowcount(dwcareader)

    # Close the archive    
    dwcareader.close()
    
    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = ['outputfile', 'delimiter', 'rowcount', 'failedrowcount']
    returnvals = [outputfile, delimiter, rowcount, failedrowcount]
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
    parser.add_option("-d", "--delimiter", dest="delimiter",
                      help="Field delimiter for the output file",
                      default=None)
    parser.add_option("-q", "--quotechar", dest="quotechar",
                      help="Quote character for the output file",
                      default=None)
    parser.add_option("-s", "--quoting", dest="quoting",
                      help="Quote style for the output file",
                      default=None)
    parser.add_option("-t", "--type", dest="type",
                      help="Type of Darwin Core archive ('gbif', 'standard')",
                      default=None)
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="The level at which to log",
                      default='INFO')
    return parser.parse_args()[0]

def main():
    global dwcafile, outputfile, archivetype
    options = _getoptions()
    dwcafile = options.inputfile
    outputfile = options.outputfile
    delimiter = options.delimiter
    quotechar = options.quotechar
    quoting = options.quoting
    archivetype = options.type
    loglevel = options.loglevel
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
    if dwcafile is None:
        print 'syntax: python dwca_core_extractor.py -l INFO -d , -i ../../data/dwca-uwymv_herp.zip -o testout.tsv -t standard'
        return
    if outputfile is None:
        outputfile = 'dwca_core_extractor_output.tsv'
    if delimiter is None:
        delimiter = '\t'
    if quotechar is None:
        quotechar = ''
    if quoting is None:
        quoting = 'NONE'
    if archivetype is None:
        type = 'standard'

    logging.debug('dwcafile: %s\noutputfile: %s\ndelimiter: %s\narchivetype: %s' %
        (dwcafile, outputfile, delimiter, archivetype) )

    inputs = {}
    inputs['dwcafile'] = dwcafile
    inputs['outputfile'] = outputfile
    inputs['delimiter'] = delimiter
    inputs['quotechar'] = quotechar
    inputs['quoting'] = quoting
    inputs['archivetype'] = archivetype
    logging.debug('inputs: %s' % inputs)
    logging.debug('json.dumps(inputs): %s' % json.dumps(inputs))

    # Write the core to a delimited outputfile
    response = json.loads(dwca_core_extractor(json.dumps(inputs)))
    
    print 'File %s with %s rows delimited with "%s", extracted from core of archive %s (type %s). %s rows failed to write.' % (response['outputfile'], response['rowcount'], delimiter, dwcafile, archivetype, response['failedrowcount'])
    print 'Response: %s' % response

if __name__ == '__main__':
    """ Demo of dwca_core_extractor """
    main()
