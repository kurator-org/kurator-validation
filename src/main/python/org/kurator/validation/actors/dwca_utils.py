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
from dwca.darwincore.utils import qualname as qn
from dwca.darwincore.terms import TERMS

geogkeytermlist = ['continent', 'country', 'stateProvince', 'county', 'municipality', 'waterBody', 'islandGroup', 'island']
taxonkeytermlist = ['kingdom', 'genus', 'subgenus', 'specificEpithet', 'infraspecificEpithet', 'scientificNameAuthorship', 'scientificName']

def dwca_metadata(dwcareader):
    """Return metadata from Darwin Core Archive Reader."""
    if dwcareader is None:
        return None

    # Pull the metadata from the archive
    # metadata is a BeautifulSoup object
    metadata=dwcareader.metadata
    return metadata

def get_core_rowcount(dwcareader):
    """Return number of rows in the core file of the Darwin Core Archive."""
    if dwcareader is None:
        return None

    rowcount=0
    # Iterate over the archive core rows to count them
    for row in dwcareader:
        # row is an instance of CoreRow
        # iteration respects the order of appearance in the core file
        rowcount=rowcount+1
    return rowcount

def get_term_valueset(dwcareader, term):
    """Return a set of unique values of a term in the core file of the Darwin Core Archive."""
    if dwcareader is None:
        return None
    if archive_has_core_term(dwcareader, term) == False:
        return None
    valueset = set()
    # Iterate over the archive core rows to count them
    for row in dwcareader:
        v = get_term_value(row.data, term)
        if v is None:
            v = get_term_value(row.data, qn(term))
        valueset.add(v)
    return valueset

def get_term_group_key(rowdata, term_list):
    """Return a constructed key from the concatenated values of a list of terms."""
    if rowdata is None:
        return None
    if term_list is None:
        return None
    key = ''
    for term in term_list:
        v = get_term_value(rowdata, term)
        if v is None:
            try:
                q = qn(term)
                v = get_term_value(rowdata, q)
            except Exception, e:
                logging.error('%s is not a Simple Darwin Core term. The search is case-sensitive.' % (term))
        if v is None:
            v = ''
        if key == '':
            key = v
        else:
            key = key + ' | ' + v
    return key 

def archive_has_core_term(dwcareader, term):
    """Return True if the core file contains a column for the term name or identifier."""
    if dwcareader is None or term is None:
        return False
    if term in dwcareader.descriptor.core.terms:
        return True
    try:
        q = qn(term)
    except Exception, e:
        logging.error('%s is not a Simple Darwin Core term. The search is case-sensitive.' % (term))
        return False
    if q in dwcareader.descriptor.core.terms:
        return True
    return False

def get_metadata_element(metadata, element_name):
    """Return an element from the metadata."""
    if metadata is None or element_name is None:
        return None
    element_value=metadata.find(element_name)
    if element_value is None:
        return None
    return element_value.string

def row_has_term(rowdata, term):
    """Return True if the row contains the term in its data dictionary by name or identifier."""
    if rowdata is None:
        return False
    if term in rowdata.keys() or qn(term) in rowdata.keys():
        return True
    return False
    
def row_has_term_value(rowdata, term):
    """Return True if the row contains a value for the term other than ''."""
    if rowdata is None:
        return False
    if term in rowdata.keys():
        if rowdata[term]!='':
            return True
    elif qn(term) in rowdata.keys():
        if rowdata[qn(term)]!='':
            return True
    return False
    
def get_term_value(rowdata, term):
    """Return the value of the term in the given rowdata."""
    if rowdata is None:
        return None
    if term in rowdata.keys():
        return rowdata[term]
    return None
    
def shortname(qualname):
    """Return a term name from a fully qualified term identifier.

    Example::
        shortname("http://rs.tdwg.org/dwc/terms/Occurrence")  # => "Occurrence"
    """
    for t in TERMS:
        if t==qualname:
            return t.rpartition('/')[2]
    return None

def term_name_list(identifierlist):
    """Return a sorted list of term names from a list of term identifiers with 
    fully qualified names.
    """
    if identifierlist is None:
        return None
    shortlist = []
    for t in sorted(identifierlist):
        shortlist.append(shortname(t))
    return shortlist

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
    if options.dwca_file is None:
        print 'syntax: dwca_metadata.py -f dwca_file'
        return
    dwcareader = DwCAReader(options.dwca_file)
    metadata=dwca_metadata(dwcareader)
    print 'Metadata:\n%s' % metadata

    coretermnames = term_name_list(list(dwcareader.descriptor.core.terms))
    print '\nTerms in core:\n%s' % (coretermnames)
        
    t='collectionCode'
    set_values = get_term_valueset(dwcareader, t)
    if set_values is not None:
        print '\nDistinct %s values in data set:\n%s' % (t, sorted(list(set_values)))

    print '\nGeography keys:'
    i = 0
    for row in dwcareader:
        geogkey = get_term_group_key(row.data, geogkeytermlist)
        i = i + 1
        print '%s' % (geogkey)
    print 'Count=%s' % i
    
    i = 0
    print '\nTaxonomy keys:\n'
    for row in dwcareader:
        taxonkey = get_term_group_key(row.data, taxonkeytermlist)
        i = i + 1
        print '%s' % (taxonkey)
    print 'Count=%s' % i
    
    dwcareader.close()
        
    rowcount = get_core_rowcount(dwcareader)
    print '\nCore row count:%s' % (rowcount)

if __name__ == '__main__':
    """ Demo of dwca_metadata_element script"""
    main()
