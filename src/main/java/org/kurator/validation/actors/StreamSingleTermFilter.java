/** StreamSingleTermFilter.java
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
 * @author mole
 *
 */
public class StreamSingleTermFilter extends KuratorActor {

	private static final Log logger = LogFactory.getLog(StreamSingleTermFilter.class);
	
	protected String filterKeyToMatch;
	protected String matchValue;
	protected boolean passOnMatch;
	
	/**
	 * Default constructor to satisfy Spring.
	 */
	public StreamSingleTermFilter() { 
		filterKeyToMatch = "";
		matchValue = "";
		passOnMatch = false;
	}
	
	/**
	 * Constructor to configure a stream single term filter messages in the form of a
	 * Map<String,String> on a single key in the map and a single match value on the key
	 * 
	 * @param filterKeyToMatch key in the Map of Key,Value to check for a match
	 * @param matchValue  value in the Map of Key,Value to match.
	 * @param passOnMatch behavior of the filter, if true: if there is a match pass the message
	 * on otherwise drop the message; if false: if there is a match drop the message, otherwise
	 * pass it on.
	 *  
	 */
	public StreamSingleTermFilter(String filterKeyToMatch, String matchValue, boolean passOnMatch) { 
		this.filterKeyToMatch = filterKeyToMatch;
		this.matchValue = matchValue;
		this.passOnMatch = passOnMatch;
	}
	
	@Override
	protected void onData(Object message) throws Exception {
		if (message instanceof Map) {
			try { 
			   Map<String,String> record = (Map<String,String>) message;
			   
			   if (passOnMatch) { 
				   if (record.containsKey(filterKeyToMatch) && record.get(filterKeyToMatch).equals(matchValue)) { 
					   broadcast(message);
				   } else { 
					   logger.trace("Not Matched. Dropping " + message);
				   }
			   } else { 
				   if (record.containsKey(filterKeyToMatch) && record.get(filterKeyToMatch).equals(matchValue)) { 
					   logger.trace("Matched. Dropping " + message);
				   } else { 
					   broadcast(message);
				   }
			   }
			   
    		} catch (ClassCastException e) { 
    			logger.error("Message was a Map, but unable to cast to Map<String,Stringt>.");
    			logger.error(e.getMessage(),e);
    		}			   
		} 
	}
	
}
