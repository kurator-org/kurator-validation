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
__version__ = "dwcareader_utils.py 2016-10-20T16:50+02:00"

# This file contains common utility functions for dealing with the content of a Darwin
# Core archive. It is built with unit tests that can be invoked by running the script
# without any command line parameters.
#
# Example:
#
# python dwcareader_utils.py

import os.path
import glob
import unittest
import xml.etree.ElementTree as ET

# Requires the Python Darwin Core Archive Reader from 
#   https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
try:
    from dwca.read import DwCAReader
    from dwca.read import GBIFResultsReader
    from dwca.read import DwCAReader
    from dwca.read import GBIFResultsReader
    from dwca.darwincore.terms import TERMS
except ImportError:
    import warnings
    s = "The python-dwca-reader package is required.\n"
    s += "pip install python-dwca-reader\n"
    s += "$JYTHON_HOME/bin/pip install python-dwca-reader"
    warnings.warn(s)

def dwca_metadata(dwcareader):
    ''' Return metadata from Darwin Core Archive Reader.'''
    if dwcareader is None:
        return None

    # Pull the metadata from the archive
    metadata=dwcareader.metadata
    return metadata

def dwca_metadata_from_file(inputfile, archivetype=None):
    ''' Return metadata from a Darwin Core Archive file.'''
    if inputfile is None or len(inputfile.strip())==0:
        return None

    # Make an appropriate reader based on whether the archive is standard or a GBIF
    # download.
    dwcareader = None
    if archivetype=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            s = 'Unable to read GBIF archive %s. %s %s' % (inputfile, e, __version__)
            logging.error(s)
            pass
    else:
        dwcareader = DwCAReader(inputfile)

    if dwcareader is None:
        logging.debug('No viable archive found at %s. %s' % (inputfile, __version__))
        return None

    metadata = dwca_metadata(dwcareader)

    # Close the archive    
    dwcareader.close()

    return metadata

def get_core_rowcount(dwcareader):
    ''' Return number of rows in the core file of an open Darwin Core Archive.'''
    if dwcareader is None:
        return None

    rowcount=0
    # Iterate over the archive core rows to count them
    for row in dwcareader:
        # row is an instance of CoreRow
        # iteration respects the order of appearance in the core file
        rowcount=rowcount+1

    return rowcount
    
def get_core_rowcount_from_file(inputfile, archivetype=None):
    ''' Return number of rows in the core file of a Darwin Core Archive file.'''
    if inputfile is None or len(inputfile.strip())==0:
        return None
    # Make an appropriate reader based on whether the archive is standard or a GBIF
    # download.
    dwcareader = None

    if archivetype=='gbif':
        try:
            dwcareader = GBIFResultsReader(inputfile)
        except Exception, e:
            s = 'Unable to read GBIF archive %s. %s %s' % (inputfile, e, __version__)
            logging.error(s)
            pass
    else:
        dwcareader = DwCAReader(inputfile)

    if dwcareader is None:
        logging.debug('No viable archive found at %s. %s' % (inputfile, __version__))
        return None

    rowcount = get_core_rowcount(dwcareader)
    
    # Close the archive    
    dwcareader.close()
    return rowcount

def shortname(qualname):
    ''' Get a term name from a fully qualified term identifier.
    parameters:
        qualname - a fully qualified term identifier 
            (e.g., 'http://rs.tdwg.org/dwc/terms/catalogNumber')
    returns:
        qualname.rpartition('/')[2] - the term name part of the identifier 
            (e.g., 'catalogNumber')
    '''
    for t in TERMS:
        if t==qualname:
            return t.rpartition('/')[2]
    return None

def short_term_names(termlist):
    ''' Get a list of term names that are the short versions of the fully qualified 
       identifiers.
    parameters:
        termlist - a list of fully qualified term identifiers
            (e.g., 'http://rs.tdwg.org/dwc/terms/catalogNumber')
    returns:
        shortnamelist - a list of terms names without qualifications 
            (e.g., 'catalogNumber')
    '''
    shortnamelist=[]
    for i in range(len(termlist)):
        longname=termlist[i]
        sname=shortname(longname)
        if sname is None:
            shortnamelist.append(longname)
        else:
            shortnamelist.append(sname)
    return shortnamelist

class DWCAUtilsReaderFramework():
    # testdatapath is the location of the files to test with
    testdatapath = './data/tests/'
    # the archive extraction path is created by the Darwin Core archive reader and
    # should be removed when finished
    archiveextractionpath = './v/'

    # following are files used as input during the tests, don't remove these
    dwca = testdatapath + 'dwca-uwymv_herp.zip'

    # following are files output during the tests, remove these in dispose()
    #csvwriteheaderfile = testdatapath + 'test_write_header_file.csv'

    def dispose(self):
        files = glob.glob(self.archiveextractionpath + '*')
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
        if os.path.isdir(self.archiveextractionpath):
            os.rmdir(self.archiveextractionpath)
        return True

class DWCAUtilsReaderTestCase(unittest.TestCase):
    def setUp(self):
        self.framework = DWCAUtilsReaderFramework()

    def tearDown(self):
        self.framework.dispose()
        self.framework = None

    def test_source_files_exist(self):
        print 'testing source_files_exist'
        dwca = self.framework.dwca
        self.assertTrue(os.path.isfile(dwca), dwca + ' does not exist')

    def test_source_is_dwca(self):
        print 'testing source_is_dwca'
        dwca = self.framework.dwca
        dwcareader = None
        try:
            dwcareader = DwCAReader(dwca)
        except:
            dwcareader = None
        s = 'No viable Darwin Core archive found at %s' % dwca
        self.assertIsNotNone(dwcareader, s)

    def test_dwca_core_row_count(self):
        print 'testing dwca_core_row_count'
        dwca = self.framework.dwca
        rowcount = get_core_rowcount_from_file(dwca)
        self.assertEqual(rowcount, 8, 'incorrect number of rows in archive core file')

    def test_metadata(self):
        print 'testing metadata'
        inputfile = self.framework.dwca
        metadata = dwca_metadata_from_file(inputfile)
        title = metadata.find("./dataset/title").text
        #print title
        self.assertEqual(title, 'UWYMV Herpetology Collection (Arctos)', 'title incorrect from archive metadata')
        creator_position = metadata.find("./dataset/creator/positionName").text
        #print creator_position
        self.assertEqual(creator_position, 'Curator', 'creator/positionName incorrect from archive metadata')
        pubdate = metadata.find("./dataset/pubDate").text
        #print pubdate.strip()
        self.assertEqual(pubdate.strip(), '2015-03-25', 'pubDate incorrect from archive metadata')
        north = metadata.find("./dataset/coverage/geographicCoverage/boundingCoordinates/northBoundingCoordinate").text
        #print north
        self.assertEqual(north, '90', 'north geographic coverage incorrect from archive metadata')
    
if __name__ == '__main__':
    print '=== dwcareader_utils.py ==='
    unittest.main()
