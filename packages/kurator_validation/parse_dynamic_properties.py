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

__author__ = "David B. Lowery, John Wieczorek"
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "parse_dynamic_properties.py 2017-06-12T15:17-04:00"
__kurator_content_type__ = "actor"
__adapted_from__ = "actor_template.py"

from dwca_utils import response
from dwca_utils import setup_actor_logging
from dwca_utils import csv_file_dialect
import os
import logging
import uuid
import argparse
import csv
import json

def parse_dynamic_properties(options):
    ''' Actor will parse the values of the dynamic properties column of the input
        and each property as separate column in a new csv file
    options - a dictionary of parameters
        loglevel - level at which to log (e.g., DEBUG) (optional)
        workspace - path to a directory for the outputfile (optional)
        inputfile - full path to the input file (required)
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

    # Make a list of keys in the response dictionary
    returnvars = ['workspace', 'outputfile', 'success', 'message', 'artifacts']

    ### Standard outputs ###
    success = False
    message = None

    ### Custom outputs ###
    # Intialize any other output variables here so that the response calls no about them

    # Make a dictionary for artifacts left behind
    artifacts = {}

    ### Establish variables ###
    inputfile = None
    outputfile = None

    ### Required inputs ###
    try:
        workspace = options['workspace']
    except:
        workspace = './'

    try:
        inputfile = options['inputfile']
    except:
        pass

    if inputfile is None or len(inputfile)==0:
        message = 'No input file given. %s' % __version__
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    if os.path.isfile(inputfile) == False:
        message = 'Input file %s not found. %s' % (inputfile, __version__)
        returnvals = [workspace, outputfile, success, message, artifacts]
        logging.debug('message:\n%s' % message)
        return response(returnvars, returnvals)

    try:
        outputfile = options['outputfile']
    except:
        pass

    if outputfile is None or len(outputfile)==0:
        outputfile='parsed_props_'+str(uuid.uuid1())+'.csv'

    # Construct the output file path in the workspace
    outputfile = '%s/%s' % (workspace.rstrip('/'), outputfile)

    ### Optional inputs ###
    # TODO: output format (csv or tsv)

    # Do the actual work now that the preparation is complete
    success = parse_props(inputfile, outputfile)

    # Add artifacts to the output dictionary if all went well
    if success==True:
        artifacts['parsed_props_output_file'] = outputfile

    # Prepare the response dictionary
    returnvals = [workspace, outputfile, success, message, artifacts]
    logging.debug('Finishing %s' % __version__)
    return response(returnvars, returnvals)


def parse_row(row):
    propdict = {}

    # parse the value of the dynamicproperties field
    for k in row:
        if k.lower().endswith('dynamicproperties') and row[k]:
            str = row[k].strip()

            if '=' in str and ';' in str:
                # parse property string using key-value pair
                # format like k1=v1;k2=v2;...
                properties = str.split(';')
                for p in properties:
                    idx = p.find('=')

                    k = p[:idx].strip()
                    v = p[idx+1:].strip()

                    propdict[k] = v;
            elif str.startswith('{') and ':' in str:
                # parse property string from json
                propdict = json.loads(str)

    return propdict


def parse_props(inputfile, outputfile):
    ''' Function to parse the dynamic properties field values into separate columns
    parameters:
        inputfile - the full path to the input file
        outputfile - the full path to the output file
    returns:
        success - True if the task is completed, otherwise False
    '''
    functionname = 'parse_props()'

    # Check for required values
    if inputfile is None or len(inputfile)==0:
        s = 'No input file given in %s.' % functionname
        logging.debug(s)
        return False

    if outputfile is None or len(outputfile)==0:
        s = 'No output file given in %s.' % functionname
        logging.debug(s)
        return False

    # determine the csv dialect of the inputfile and create empty set for fields
    dialect = csv_file_dialect(inputfile)
    propfields = set()

    # initial parse of the csv file to collect new fields to add based
    # on values of dynamicproperties
    with open(inputfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, dialect=dialect)
        fieldnames = csvreader.fieldnames

        for row in csvreader:
            properties = parse_row(row)

            fields = set(properties.keys())
            propfields = propfields.union(fields)

    # add all the parsed properties to the list of fieldnames
    fieldnames += propfields

    # add new fields and parsed values to the end of the output csvfile
    with open(outputfile, 'w') as csvout:
        csvwriter = csv.DictWriter(csvout, fieldnames, dialect=dialect)
        csvwriter.writeheader()

        with open(inputfile, 'rb') as csvfile:
            csvreader = csv.DictReader(csvfile, dialect=dialect)

            for row in csvreader:
                properties = parse_row(row)

                row.update(properties)
                csvwriter.writerow(row)

    s = 'Parsed csv written to %s in %s.' % (outputfile, functionname)
    logging.debug(s)

    # Success
    return True

def _getoptions():
    ''' Parse command line options and return them.'''
    parser = argparse.ArgumentParser()

    help = 'full path to the input file (required)'
    parser.add_argument("-i", "--inputfile", help=help)

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

    if options.inputfile is None or len(options.inputfile)==0:
        s =  'syntax:\n'
        s += 'python parse_dynamic_properties.py'
        s += ' -i ./data/onslow.csv'
        s += ' -o output.csv'
        s += ' -w ./workspace'
        s += ' -l DEBUG'
        print '%s' % s
        return

    optdict['inputfile'] = options.inputfile
    optdict['outputfile'] = options.outputfile
    optdict['workspace'] = options.workspace
    optdict['loglevel'] = options.loglevel
    print 'optdict: %s' % optdict

    # parse the dynamic properties and append to output csv
    response=parse_dynamic_properties(optdict)
    print '\nresponse: %s' % response

if __name__ == '__main__':
    main()
