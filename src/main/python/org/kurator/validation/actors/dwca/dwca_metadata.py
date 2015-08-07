#!/usr/bin/env python

# Copyright 2015 President and Fellows of Harvard College
#
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

import logging
from optparse import OptionParser

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
from dwca.read import DwCAReader

def dwca_metadata(dwca_file):
    """Open a Darwin Core archive and return the metadata."""
    # Open the Darwin Core Archive given in dwca_file
    dwca = DwCAReader(dwca_file)
    if not dwca:
        return None
        
    # Pull the metadata from the archive
    metadata=dwca.metadata
    
    # Close the archive to free resources
    dwca.close()
    
    return metadata

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-f", "--dwca_file", dest="dwca_file",
                      help="Darwin Core Archive file",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    logging.info('options %s' % options)
    if options.dwca_file is None:
        print 'syntax: dwca_metadata.py -f dwca_file'
        return

    logging.info('dwca_file %s' % options.dwca_file)
    metadata=dwca_metadata(options.dwca_file)
    print metadata.prettify()
    
if __name__ == '__main__':
    """ Demo of dwca_metadata script"""
    main()
