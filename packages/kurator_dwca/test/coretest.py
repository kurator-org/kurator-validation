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

import setup_env
setup_env.fix_sys_path()

from geomancer.core import *
from geomancer import constants

import math
import logging
import os
import unittest
import simplejson

class TestGeomancer(unittest.TestCase):
    
    def test_distanceunits(self):
        distunits = constants.DistanceUnits.all()
        for unit in distunits:
            logging.info(unit)

    def test_headings(self):
        headings = constants.Headings.all()
        for heading in headings:
            logging.info(heading)

    def test_datums(self):
        datums = constants.Datums.all()
        for datum in datums:
            logging.info(datum)

    def test_point2wgs84(self):
        agd66point = Point(144.966666667, -37.8)
        wgs84point = agd66point.point2wgs84(Datums.AGD84)
        logging.info(wgs84point)
        logging.info(Datums.AGD84)
    #    144.96797984155188, -37.798491994062296
    #    144.96798640000000, -37.798480400000000

    def test_distanceprecision(self):
        d = '110'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        
        d = '0'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        d = '1'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '2'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '9'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '11'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '12'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '19'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '20'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '21'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '49'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '50'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '51'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '99'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '100'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '101'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '109'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '110'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '111'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '149'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '150'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '151'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '199'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '200'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '201'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '210'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '999'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '1000'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
    
        
        d = '10.000'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.001'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.00'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.01'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.0'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.1'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.9'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.125'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.25'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.3333'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '10.5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.625'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.75'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.5'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        d = '0.66667'
        p = getDistancePrecision(d)
        logging.info(d+" "+str(p))
        
#    def test_georeference_feature(self):
#        geocode = get_example_geocode()
#        georef = georef_feature(geocode)
#        logging.info('Georeference: %s'%(georef))
    
    def test_point_from_dist_at_bearing(self):
        point = Point(0,0)
        distance = 1000000
        bearing = 45 
        endpoint = point.get_point_from_distance_at_bearing(distance, bearing)
        logging.info("%s meters at bearing %s from %s, %s: %s"%(distance, bearing, point.lng, point.lat, endpoint) )
        
    def test_haversine_distance(self):
        point = Point(0,0)
        distance = 1000000
        bearing = 45 
        endpoint = point.get_point_from_distance_at_bearing(distance, bearing)
        hdist = point.haversine_distance(endpoint)
        logging.info("%s meters"%(hdist) )
        diff = math.fabs(distance - hdist) 
        if diff >= 0.5:
            logging.info("FAIL: test_haversine_distance(): difference = %s meters"%(diff) )
        else:
            logging.info("PASS: test_haversine_distance(): difference = %s meters"%(diff) )        

    def test_truncate(self):
        self.assertEqual(truncate(60,0), '60')
        self.assertEqual(truncate(60.0000,0), '60')
        self.assertEqual(truncate(60.0000000001,0), '60')
        self.assertEqual(truncate(60.0000000001,4), '60')
        self.assertEqual(truncate(0.9666666667,4), '0.9667')

    def test_has_num(self):
        self.assertEqual(has_num('6'), 0)
        self.assertEqual(has_num('km'), None)
        self.assertEqual(has_num('6km'), 0)
        self.assertEqual(has_num('km6'), 2)
        self.assertEqual(has_num('1/2'), 0)

    def test_parse_loc(self):
        p=parse_loc('5 mi N Ft. Bragg', 'foh')
        self.assertEqual(p['verbatim_loc'],'5 mi N Ft. Bragg')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'5')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'5 mi N Ft. Bragg')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(len(p['features']),1)
        p['features'].remove('Ft. Bragg')
        self.assertEqual(len(p['features']),0)
        
        p=parse_loc('99 Palms 500 ft. N', 'foh')
        self.assertEqual(p['verbatim_loc'],'99 Palms 500 ft. N')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'500')
        self.assertEqual(p['offset_unit'],'ft')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'500 ft N 99 Palms')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'99 Palms')

        p=parse_loc('500 ft. N 99 Palms', 'foh')
        self.assertEqual(p['verbatim_loc'],'500 ft. N 99 Palms')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'500')
        self.assertEqual(p['offset_unit'],'ft')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'500 ft N 99 Palms')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'99 Palms')

        p=parse_loc('South Haven 6 km west', 'foh')
        self.assertEqual(p['verbatim_loc'],'South Haven 6 km west')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'6')
        self.assertEqual(p['offset_unit'],'km')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'6 km W South Haven')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'South Haven')

        p=parse_loc('6km west Berkeley', 'foh')
        self.assertEqual(p['verbatim_loc'],'6km west Berkeley')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'6')
        self.assertEqual(p['offset_unit'],'km')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'6 km W Berkeley')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Berkeley')

        p=parse_loc('5 1/2 miles NE of Berkeley', 'foh')
        self.assertEqual(p['verbatim_loc'],'5 1/2 miles NE of Berkeley')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'5.5')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'NE')
        self.assertEqual(p['interpreted_loc'],'5.5 mi NE Berkeley')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Berkeley')

        p=parse_loc('7 mi W up 6-mile creek', 'foh')
        self.assertEqual(p['verbatim_loc'],'7 mi W up 6-mile creek')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'7')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'7 mi W 6-mile creek')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'6-mile creek')

        p=parse_loc('7 mi W 10 Mile','foh')
        self.assertEqual(p['verbatim_loc'],'7 mi W 10 Mile')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'7')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'7 mi W 10 Mile')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'10 mile')

        p=parse_loc('6 Mile Creek 7 mi W','foh')
        self.assertEqual(p['verbatim_loc'],'6 Mile Creek 7 mi W')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'7')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'7 mi W 6 Mile Creek')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'6 Mile Creek')

        p=parse_loc('7 mi W N fork 6 Mile Creek','foh')
        self.assertEqual(p['verbatim_loc'],'7 mi W N fork 6 Mile Creek')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'7')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'W')
        self.assertEqual(p['interpreted_loc'],'7 mi W N fork 6 Mile Creek')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'N fork 6 Mile Creek')

        p=parse_loc('10 miles North of Gaastra', 'foh')
        self.assertEqual(p['verbatim_loc'],'10 miles North of Gaastra')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('10 mi. N from Gaastra', 'foh')
        self.assertEqual(p['verbatim_loc'],'10 mi. N from Gaastra')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('10 mi N Gaastra', 'foh')
        self.assertEqual(p['verbatim_loc'],'10 mi N Gaastra')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('10mi north Gaastra', 'foh')
        self.assertEqual(p['verbatim_loc'],'10mi north Gaastra')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('10mi. N Gaastra', 'foh')
        self.assertEqual(p['verbatim_loc'],'10mi. N Gaastra')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('Gaastra 10 mi N', 'foh')
        self.assertEqual(p['verbatim_loc'],'Gaastra 10 mi N')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')

        p=parse_loc('Gaastra 10mi. N', 'foh')
        self.assertEqual(p['verbatim_loc'],'Gaastra 10mi. N')
        self.assertEqual(p['locality_type'],'foh')
        self.assertEqual(p['offset_value'],'10')
        self.assertEqual(p['offset_unit'],'mi')
        self.assertEqual(p['heading'],'N')
        self.assertEqual(p['interpreted_loc'],'10 mi N Gaastra')
        self.assertEqual(p['status'],'complete')
        self.assertEqual(p['features'][0],'Gaastra')
       
    def test_final_georef(self):
        localities = []
        loc_b = parse_loc('5 mi SW Berkeley', 'foh')
        loc_a = parse_loc('Alameda County', 'f')
        loc_c = parse_loc('CA', 'f')
        localities.append(loc_a)
        localities.append(loc_b)
        localities.append(loc_c)
        a = loc_a['features'][0].strip(' County')
        b = loc_b['features'][0]
        c = loc_c['features'][0]
        loc_a['feature_geocodes'] = GeocodeResultParser.get_feature_geoms(a, test_response_alameda)
        loc_b['feature_geocodes'] = GeocodeResultParser.get_feature_geoms(b, test_response_berkeley)
        loc_c['feature_geocodes'] = GeocodeResultParser.get_feature_geoms(c, test_response_ca)
        final_georefs = loc_georefs(localities)
        pass

    def test_bb_kml(self):
        nw = Point(-117.851,35.301)
        se = Point(-117.85,35.3)
        bb = BoundingBox(nw,se)
        kml = bb.to_kml()
        pass

def get_example_geocode():
    """Returns an Google Geocoding JSON response for "Mountain View"."""
    geocode = simplejson.loads("""{
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Mountain View",
               "short_name" : "Mountain View",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "San Jose",
               "short_name" : "San Jose",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "Santa Clara",
               "short_name" : "Santa Clara",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Mountain View, CA, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.4698870,
                  "lng" : -122.0446720
               },
               "southwest" : {
                  "lat" : 37.35654100000001,
                  "lng" : -122.1178620
               }
            },
            "location" : {
               "lat" : 37.38605170,
               "lng" : -122.08385110
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.42150620,
                  "lng" : -122.01982140
               },
               "southwest" : {
                  "lat" : 37.35058040,
                  "lng" : -122.14788080
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}""")
    return geocode

test_response_ca = {
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "California, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 42.00951690,
                  "lng" : -114.1312110
               },
               "southwest" : {
                  "lat" : 32.5288320,
                  "lng" : -124.4820030
               }
            },
            "location" : {
               "lat" : 36.7782610,
               "lng" : -119.41793240
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 41.21563630,
                  "lng" : -111.22213140
               },
               "southwest" : {
                  "lat" : 32.06836610,
                  "lng" : -127.61373340
               }
            }
         },
         "types" : [ "administrative_area_level_1", "political" ]
      }
   ],
   "status" : "OK"
}

test_response_alameda = {
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Alameda",
               "short_name" : "Alameda",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Alameda, California, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.90582390,
                  "lng" : -121.4692140
               },
               "southwest" : {
                  "lat" : 37.45453890,
                  "lng" : -122.3737820
               }
            },
            "location" : {
               "lat" : 37.60168920,
               "lng" : -121.71954590
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.8840360,
                  "lng" : -121.20730830
               },
               "southwest" : {
                  "lat" : 37.31826680,
                  "lng" : -122.23178350
               }
            }
         },
         "types" : [ "administrative_area_level_2", "political" ]
      }
   ],
   "status" : "OK"
}

test_response_berkeley = {
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Alameda",
               "short_name" : "Alameda",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "California",
               "short_name" : "CA",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Berkeley, CA, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 37.90582390,
                  "lng" : -122.2341790
               },
               "southwest" : {
                  "lat" : 37.8357270,
                  "lng" : -122.3677810
               }
            },
            "location" : {
               "lat" : 37.87159260,
               "lng" : -122.2727470
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 37.90681610,
                  "lng" : -122.20871730
               },
               "southwest" : {
                  "lat" : 37.83635220,
                  "lng" : -122.33677670
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Ocean",
               "short_name" : "Ocean",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "New Jersey",
               "short_name" : "NJ",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Berkeley, NJ, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.07674290
               },
               "southwest" : {
                  "lat" : 39.756830,
                  "lng" : -74.3292630
               }
            },
            "location" : {
               "lat" : 39.89719960,
               "lng" : -74.18271190
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.07674290
               },
               "southwest" : {
                  "lat" : 39.756830,
                  "lng" : -74.3292630
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Holiday City-Berkeley",
               "short_name" : "Holiday City-Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Ocean",
               "short_name" : "Ocean",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "New Jersey",
               "short_name" : "NJ",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Holiday City-Berkeley, NJ, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.2403250
               },
               "southwest" : {
                  "lat" : 39.9415410,
                  "lng" : -74.3224790
               }
            },
            "location" : {
               "lat" : 39.96457970,
               "lng" : -74.27075090
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 39.9873730,
                  "lng" : -74.2403250
               },
               "southwest" : {
                  "lat" : 39.9415410,
                  "lng" : -74.3224790
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Proviso",
               "short_name" : "Proviso",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "Cook",
               "short_name" : "Cook",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "Illinois",
               "short_name" : "IL",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            }
         ],
         "formatted_address" : "Berkeley, IL, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 41.899830,
                  "lng" : -87.89541290
               },
               "southwest" : {
                  "lat" : 41.87309590,
                  "lng" : -87.92061090
               }
            },
            "location" : {
               "lat" : 41.88891940,
               "lng" : -87.90339560
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 41.899830,
                  "lng" : -87.89541290
               },
               "southwest" : {
                  "lat" : 41.87309590,
                  "lng" : -87.92061090
               }
            }
         },
         "types" : [ "locality", "political" ]
      },
      {
         "address_components" : [
            {
               "long_name" : "Berkeley",
               "short_name" : "Berkeley",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "Norwood",
               "short_name" : "Norwood",
               "types" : [ "administrative_area_level_3", "political" ]
            },
            {
               "long_name" : "St Louis",
               "short_name" : "St Louis",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "Missouri",
               "short_name" : "MO",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            },
            {
               "long_name" : "63145",
               "short_name" : "63145",
               "types" : [ "postal_code" ]
            }
         ],
         "formatted_address" : "Berkeley, MO 63145, USA",
         "geometry" : {
            "bounds" : {
               "northeast" : {
                  "lat" : 38.773750,
                  "lng" : -90.3105690
               },
               "southwest" : {
                  "lat" : 38.7197740,
                  "lng" : -90.3533350
               }
            },
            "location" : {
               "lat" : 38.75449520,
               "lng" : -90.33122560
            },
            "location_type" : "APPROXIMATE",
            "viewport" : {
               "northeast" : {
                  "lat" : 38.773750,
                  "lng" : -90.3105690
               },
               "southwest" : {
                  "lat" : 38.7197740,
                  "lng" : -90.3533350
               }
            }
         },
         "types" : [ "locality", "political" ]
      }
   ],
   "status" : "OK"
}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
