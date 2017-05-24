/** EnvironmentTagger.java
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
package org.kurator.validation.actors;

import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.kurator.akka.KuratorActor;

/**
 * Tags occurrence records with inferences about the marine/non-marine environment.
 * 
 * @author mole
 *
 */
public class EnvironmentTagger extends KuratorActor {
	
	private static final long serialVersionUID = 1L;
	private static final Log logger = LogFactory.getLog(EnvironmentTagger.class);

	/* (non-Javadoc)
	 * @see org.kurator.akka.KuratorActor#onData(java.lang.Object)
	 */
	@Override
	protected void onData(Object message) throws Exception {
		if (message instanceof Map) {
			try { 
			   Map<String,String> record = (Map<String,String>) message;
			   
			   if (record.containsKey("waterBody")) { 
				   String waterBody = record.get("waterBody");
				   if (waterBody.contains("Ocean")) { 
					   record.put("isMarine", "true");
				   }
			   }
			   if (record.containsKey("country")) { 
				   String country = record.get("country");
				   if (country.trim().equalsIgnoreCase("High Seas")) { 
					   record.put("isMarine", "true");
				   }
			   }
			   if (record.containsKey("higherGeography")) { 
				   String higherGeog = record.get("higherGeography");
				   if (higherGeog.matches(".*(Atlantic|Pacific|Arctic|Indian|Southern) Ocean.*")) { 
					   record.put("isMarine", "true");
				   }
			   }
			   if (!record.containsKey("isMarine")) { 
				   record.put("isMarine", "false");
			   }
			   logger.debug("isMarine=" + record.get("isMarine"));
			   broadcast(record);
			   
			} catch (ClassCastException e) { 
				logger.debug(e.getMessage());
			}
		}
		
	}

}
