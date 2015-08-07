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

gfilename = "../../data/dwca-uwymv_herp.zip"

import logging
from optparse import OptionParser

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
from dwca.read import DwCAReader
from dwca_utils import get_term_group_key
from dwcaterms import geogkeytermlist

def read_core_rows():
    # The with statement ensures resources will be properly cleaned after leaving the 
    # block - after all yields have completed.
    with DwCAReader(gfilename) as dwca:
        for core_row in dwca:
            yield core_row

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-f", "--dwca_file", dest="dwca_file",
                      help="Darwin Core Archive file",
                      default=None)
    return parser.parse_args()[0]

def main():
    global gfilename 
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    if options.dwca_file is None:
        print 'syntax: dwca_reader.py -f dwca_file using %s' % gfilename
#        return
    else:
        gfilename = options.dwca_file
        
    print '\nGeography keys:'
    i = 0
    for row in read_core_rows():
        geogkey = get_term_group_key(row.data, geogkeytermlist)
        i = i + 1
        print '%s' % (geogkey)
    print 'Count=%s' % i

if __name__ == '__main__':
    """ Demo of dwca_utils functions"""
    main()
