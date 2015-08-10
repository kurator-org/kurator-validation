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

import csv

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader

from dwca.read import DwCAReader
from dwca.read import GBIFResultsReader
from dwca.darwincore.utils import qualname as qn
from dwca.darwincore.terms import TERMS
from dwcaterms import geogkeytermlist
from dwcaterms import taxonkeytermlist

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
        
def standardize_term(dwcareader, changeterm, lookupdict):
    if dwcareader is None or changeterm is None or lookupdict is None:
        return None
        
    newvalues=set()
    for row in dwcareader:
        shouldbe=None
        was=get_term_value(row.data, changeterm)
        if was not in newvalues:
            shouldbe=get_standard_value(was, lookupdict)
            if shouldbe is None:
                newvalues.add(was)
            elif was!=shouldbe:
                set_term_value(row.data, changeterm, shouldbe)
    return newvalues

def append_to_vocab(filename, newtermlist):
    """Add values to a lookup dictionary file."""
    dialect = None
    with open(filename, 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
    dialect.lineterminator='\r'

    with open(filename, 'a') as csvfile:
        fieldnames=['verbatim','standard','checked']
        writer = csv.DictWriter(csvfile, dialect=dialect, quoting=csv.QUOTE_NONNUMERIC, fieldnames=fieldnames)
        for term in newtermlist:
            if term is not None:
                writer.writerow({'verbatim':term, 'standard':'', 'checked':0 })

def get_dict_for_vocab(filename):
    """Create a lookup dictionary for standard values of a term."""
    dict={}
    dialect = None
    with open(filename, 'rb') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
    dialect.lineterminator='\r'
    with open(filename) as csvfile:
        dr = csv.DictReader(csvfile, dialect=dialect, quoting=csv.QUOTE_NONNUMERIC)
        for row in dr:
            verbatim=row['verbatim']
            standard=row['standard']
            dict[verbatim]=standard
    return dict

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
        # Try to find the value of the term in the rowdata, even using the fully 
        # qualified version of the term name.
        v = get_term_value(rowdata, term)
        if v is None:
            # Could not find the term in the rowdata, even using the qualified name.
            v = ''
        if key == '':
            # If this is the first term in the key group.
            key = v
        else:
            # For subsequent terms in the key group
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
        logging.error('archive_has_core_term(): %s is not a Simple Darwin Core term. The search is case-sensitive.' % (term))
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
    
def set_term_value(rowdata, term, value):
    """Set the value of the term in the given rowdata."""
    if rowdata is None:
        return
    if term in rowdata.keys():
        rowdata[term]=value
    elif qn(term) in rowdata.keys():
        rowdata[qn(term)]=value
    return

def get_term_value(rowdata, term):
    """Return the value of the term in the given rowdata."""
    if rowdata is None:
        return None
    if term in rowdata.keys():
        return rowdata[term]
    # Try a Darwin Core fully qualified term if it wasn't found as is.
    try:
        q=qn(term)
    except Exception, e:
        return None
    if q in rowdata.keys():
        return rowdata[q]
    return None

def get_standard_value(was, valuedict):
    """Return a standard value from the valuedict."""
    if was is None:
        return None
    if was in valuedict.keys():
        return valuedict[was]
    return None

# def standardize_term_value(rowdata, term, valuedict):
#     """Replace the value of the term in rowdata with the value from the valuedict."""
#     was=None
#     shouldbe=None
#     if rowdata is None:
#         return False
#     if term is None:
#         return False
#     if term in rowdata.keys():
#         was=rowdata[term]
#     elif qn(term) in rowdata.keys():
#         was=rowdata[qn(term)]
#     if was is not None:
#     	shouldbe=valuedict[was]
#     	if was!=shouldbe:
#             rowdata[term]=shouldbe
#             print 'was: %s shouldbe: %s' % (was, shouldbe)
#             return True
#     return False
#     
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
    parser.add_option("-t", "--archive_type", dest="archive_type",
                      help="Darwin Core Archive file type. None or 'gbif'",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    if options.dwca_file is None:
        print 'syntax: dwca_utils.py -f dwca_file'
        return
    dwcareader = None
    if options.archive_type=='gbif':
        dwcareader = GBIFResultsReader(options.dwca_file)
    else:
        dwcareader = DwCAReader(options.dwca_file)
    if dwcareader is None:
        print 'No archive found at %s' % options.dwca_file

    rowcount = get_core_rowcount(dwcareader)
    print '\nCore row count:%s' % (rowcount)

    metadata=dwca_metadata(dwcareader)
    print 'Metadata:\n%s' % metadata

    coretermnames = term_name_list(list(dwcareader.descriptor.core.terms))
    print '\nTerms in core:\n%s' % (coretermnames)
        
    t='establishmentMeans'
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

#     i = 0
#     changed=0
#     changeterm='establishmentMeans'
#     em_dict=get_dict_for_vocab('../../vocabularies/establishmentMeans.csv')
#     print 'establishmentMeans dict:\n %s' % em_dict
#     for row in dwcareader:
#         if standardize_term_value(row.data, changeterm, em_dict) is True:
#             changed=changed+1
#         i = i + 1
#     print 'Count=%s %s changed %s times' % (i, changeterm, changed)
#     
#     i = 0
#     changed=0
#     changeterm='basisOfRecord'
#     bor_dict=get_dict_for_vocab('../../vocabularies/basisOfRecord.csv')
#     print 'basisOfRecord dict:\n %s' % bor_dict
#     for row in dwcareader:
#         if standardize_term_value(row.data, changeterm, bor_dict) is True:
#             changed=changed+1
#         i = i + 1
#     print 'Count=%s %s changed %s times' % (i, changeterm, changed)

    changeterm='basisOfRecord'
    vocab_file='../../vocabularies/basisOfRecord.csv'
    vdict=get_dict_for_vocab(vocab_file)
    newvalues=standardize_term(dwcareader, changeterm, vdict)
    print 'Append these to %s newvalues=%s' % (vocab_file, newvalues)
    if newvalues is not None:
        append_to_vocab(vocab_file, newvalues)

    changeterm='institutionCode'
    vocab_file='../../vocabularies/icode.csv'
    vdict=get_dict_for_vocab(vocab_file)
    newvalues=standardize_term(dwcareader, changeterm, vdict)
    print 'Append these to %s newvalues=%s' % (vocab_file, newvalues)
    if newvalues is not None:
        append_to_vocab(vocab_file, newvalues)
    
    dwcareader.close()

if __name__ == '__main__':
    """ Demo of dwca_utils functions"""
    main()
