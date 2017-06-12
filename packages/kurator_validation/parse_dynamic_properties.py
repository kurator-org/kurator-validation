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

__author__ = "David B. Lowery"
__copyright__ = "Copyright 2017 President and Fellows of Harvard College"
__version__ = "parse_dynamic_properties.py 2017-06-12T13:21-04:00"
__kurator_content_type__ = "utility"
__adapted_from__ = ""

from dwca_utils import csv_file_dialect
import csv
import json

def parseProperties(str):
    str = str.strip()

    propdict = {}

    if '=' in str and ';' in str:
        # parse property string using key-value pair
        # format like k1=v1;k2=v2;...
        properties = str.split(';')
        for p in properties:
            prop = p.split('=')

            k = prop[0].strip()
            v = prop[1].strip()

            propdict[k] = v;
    elif str.startswith('{') and ':' in str:
        # parse property string from json
        propdict = json.loads(str)

    return propdict

def main():
    dialect = csv_file_dialect('./onslow.csv')
    propfields = set()

    # initial parse of the csv file to collect new fields to add based
    # on values of dynamicproperties
    with open('./onslow.csv', 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, dialect=dialect)
        fieldnames = csvreader.fieldnames

        for row in csvreader:

            for k in row:
                if k.lower().endswith('dynamicproperties') and row[k]:
                    properties = parseProperties(row[k])

                    for k in properties.keys():
                        propfields.add(k)

    fieldnames += propfields

    # add new fields and parsed values to the end of the output csvfile
    with open('./output.csv', 'w') as csvout:
        csvwriter = csv.DictWriter(csvout, fieldnames, dialect=dialect)
        csvwriter.writeheader()

        with open('./onslow.csv', 'rb') as csvfile:
            csvreader = csv.DictReader(csvfile, dialect=dialect)

            for row in csvreader:
                properties = { }

                for k in row:
                    if k.lower().endswith('dynamicproperties') and row[k]:
                        properties = parseProperties(row[k])

                row.update(properties)

                csvwriter.writerow(row)

if __name__ == '__main__':
    main()
