/** StreamMerge.java
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

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.kurator.akka.KuratorActor;
import org.kurator.akka.messages.EndOfStream;

/**
 * @author mole
 *
 */
public class StreamMerge extends KuratorActor {

	private static final Log logger = LogFactory.getLog(StreamMerge.class);
	
	private int listensTo = 1;
	private int eosHeard = 0;
	
	public StreamMerge() { 
		eosHeard = 0;
		listensTo = inputs.size();
	}
	
	public StreamMerge(int numberOfInputs) { 
		eosHeard = 0;
		listensTo = numberOfInputs;
	}
	
	/**
	 * 
	 */
    protected void onEndOfStream(EndOfStream eos) throws Exception {
    	logger.debug(inputs.size());
    	logger.debug(eosHeard);
    	logger.debug(listensTo);
        logger.trace("StreamMerge ON_END_OF_STREAM_EVENT ("+ eosHeard + " of " + listensTo +") heard.");
        if (endOnEos && eosHeard>=listensTo) {
        	logger.trace("StreamMerge ON_END_OF_STREAM_EVENT handler invoked.");
            endStreamAndStop(eos);
        }
    }	
    
	protected void onData(Object message) throws Exception {
		broadcast(message);
	}
}
