/** SimpleWoRMSGuidLookup.java
 *
 * Copyright 2017 President and Fellows of Harvard College
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.kurator.validation.actors.mapstream;

import java.util.Map;

import org.filteredpush.qc.date.DateUtils;
import org.filteredpush.qc.sciname.SciNameUtils;
import org.kurator.akka.KuratorActor;

/**
 * @author mole
 *
 */
public class SimpleWoRMSGuidLookup extends KuratorActor {
	
	@Override
	protected void onData(Object message) throws Exception {
		if (message instanceof Map) {
			try { 
			   Map<String,String> record = (Map<String,String>) message;
				if (record.containsKey("scientificName")) { 
					String scientificName = record.get("scientificName");
					String scientificNameAuthorship = record.get("scientificNameAuthorship");
					logger.value("Looking Up: " + scientificName + ":" + scientificNameAuthorship); 
					String guid =  SciNameUtils.simpleWoRMSGuidLookup(scientificName, scientificNameAuthorship);
					logger.value("Found GUID: " + guid);
                                        if (guid==null || guid.isEmpty()) {
                                                record.put("taxonID", " ");
                                        }
					if (!DateUtils.isEmpty(guid)) { 
						if (DateUtils.isEmpty(record.get("taxonID"))) { 
						    record.put("taxonID", guid);
						}
					}
				}
    		} catch (ClassCastException e) { 
    			logger.error("Message was a Map, but unable to cast to Map<String,Stringt>.");
    			logger.error(e.getMessage());
    		}			   
		} 
		broadcast(message);
	}	

}
