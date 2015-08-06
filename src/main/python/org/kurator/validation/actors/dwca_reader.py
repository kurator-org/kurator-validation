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

# Python Darwin Core Archive Reader from 
# https://github.com/BelgianBiodiversityPlatform/python-dwca-reader
# pip install python-dwca-reader
from dwca.read import DwCAReader

filename=None

def read_file():
    # The with statement ensures resources will be properly cleaned after leaving the block
    with DwCAReader(filename) as dwca:
        for core_row in dwca:
            yield core_row.data
