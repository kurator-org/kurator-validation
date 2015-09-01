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
__author__ = "Aaron Steele"
__copyright__ = "Copyright 2011 University of California at Berkeley"

"""This module provides unit testing for Bounding Box class."""

import logging
import sys
import unittest

sys.path.insert(0, '../')

from geomancer.bb import BoundingBox
from geomancer.point import *

class BBTest(unittest.TestCase):
    def test_center(self):
        nwcorner = Point(0, 0)
        secorner = Point(10, 0)
        bb=BoundingBox(nwcorner,secorner)
        center=bb.center()
        self.assertEqual(center.lat,0)
        self.assertEqual(float(truncate(center.lng,DEGREE_DIGITS)),5)
        
        nwcorner = Point(0, 10)
        secorner = Point(10, 0)
        bb=BoundingBox(nwcorner,secorner)
        center=bb.center()
        self.assertEqual(float(truncate(center.lat,DEGREE_DIGITS)),5.0190007)
        self.assertEqual(float(truncate(center.lng,DEGREE_DIGITS)),5.0383688)

    def test_intersection(self):
        bb0=BoundingBox.create(0,10,10,0)
        bb1=BoundingBox.create(5,15,15,5)
        bb2=BoundingBox.create(7,8,8,7)
        bb_list = [bb0,bb1,bb2]
        i = BoundingBox.intersect_all(bb_list)
        self.assertEqual(i.nw.get_lng(), 7)
        self.assertEqual(i.nw.get_lat(), 8)
        self.assertEqual(i.se.get_lng(), 8)
        self.assertEqual(i.se.get_lat(), 7)
        print 'nw: %s se: %s' % (i.nw, i.se)
        
        nwcorner = Point(0, 10)
        secorner = Point(10, 0)
        bb1=BoundingBox(nwcorner,secorner)
        nwcorner = Point(5, 15)
        secorner = Point(15, 5)
        bb2=BoundingBox(nwcorner,secorner)
        i = bb1.intersection(bb2)
        self.assertEqual(i.nw.get_lng(), 5)
        self.assertEqual(i.nw.get_lat(), 10)
        self.assertEqual(i.se.get_lng(), 10)
        self.assertEqual(i.se.get_lat(), 5)
        print 'nw: %s se: %s' % (i.nw, i.se)

        nwcorner = Point(170, 10)
        secorner = Point(-170, -10)
        bb1=BoundingBox(nwcorner,secorner)
        nwcorner = Point(-175, 5)
        secorner = Point(-165, -5)
        bb2=BoundingBox(nwcorner,secorner)
        i = bb1.intersection(bb2)
        self.assertEqual(i.nw.get_lng(), -175)
        self.assertEqual(i.nw.get_lat(), 5)
        self.assertEqual(i.se.get_lng(), -170)
        self.assertEqual(i.se.get_lat(), -5)
        print 'nw: %s se: %s' % (i.nw, i.se)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
