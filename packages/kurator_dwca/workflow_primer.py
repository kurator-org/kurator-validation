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
__copyright__ = "Copyright 2015 President and Fellows of Harvard College"
__version__ = "workflow_primer.py 2015-09-03T23:05:55+02:00"

import json

wfparameter=None
wfvalue=None

def workflow_primer():
    """Take a global variable and return it from a function call. Allows a workflow to
        be started with a Workflow_primer and parameters to pass to a first actor that
        requires parameters."""
    global wfparameter, wfvalue
    # Successfully completed the mission
    # Return a dict of important information as a JSON string
    response = {}
    returnvars = [wfparameter]
    returnvals = [wfvalue]
    i=0
    for a in returnvars:
        response[a]= returnvals[i] 
        i+=1
    return json.dumps(response)
