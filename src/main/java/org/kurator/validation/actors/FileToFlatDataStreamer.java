package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.kurator.akka.KuratorActor;
import org.kurator.exceptions.KuratorException;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;

/**
 * Actor that can take as input (in onData()) an options map containing a reference to a workspace 
 * and a a csv or tsv file name (as outputfile) with a header, and then broadcasts as a stream each
 * line of the provided file (in a map where headers of the csv are keys and the cell values are values).
 * The provided file must have at least two columns.
 * 
 * @author mole
 */
public class FileToFlatDataStreamer extends KuratorActor {
	
    protected CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();
    protected CSVFormat tsvFormat = CSVFormat.TDF.withHeader();
    protected CSVFormat pipeFormat = CSVFormat.newFormat('|').withIgnoreSurroundingSpaces(true).withHeader();
    
    private Map<String,String> filesReading = null;

    /**
     * Expects a message consisting of an object that can be cast into Map<String,Object>.
     * Where the string keys include at least workspace and outputfile (where outputfile
     * is the file name for the input csv file to be streamed.
     */
    @Override
    protected void onData(Object data) throws Exception {
    	
    	if (filesReading==null) { 
    		filesReading = new HashMap<String,String>();
    	}
    	
    	if (data instanceof Map) { 

    		Map<String, Object> options = null;
    		try { 
    			options = (Map<String, Object>) data;

    			String workspaceName = (String) options.get("workspace");
    			String inputfileName = (String) options.get("outputfile"); // output from upstream, input for this actor

    			logger.debug(workspaceName);
    			logger.debug(inputfileName);
    			
    			if (inputfileName == null) { 
    				throw new FileNotFoundException("Error: Unable to read upstream file source, no filename provided");
    			} 

    			File workspace = new File(workspaceName);
    			File inputfile = new File(inputfileName);

    			if (inputfile.exists() && inputfile.canRead()) { 
    				if (filesReading.containsKey(inputfileName)) {
    					logger.debug("Allready reading input file:" + inputfileName);
    			    } else { 
    				filesReading.put(inputfileName, inputfileName);
    				FileReader inputReader = new FileReader(inputfile);

    				CSVParser csvParser = new CSVParser(inputReader, tsvFormat);
    				Map<String,Integer> headerMap = csvParser.getHeaderMap();
    				if (headerMap.isEmpty() || headerMap.size()==1)  {
    					Entry<String,Integer> firstHeader = headerMap.entrySet().iterator().next();
    					if (firstHeader.getKey().contains(",")) { 
    					    csvParser = new CSVParser(inputReader, csvFormat);
    					} else if (firstHeader.getKey().contains("|")) {
    						csvParser = new CSVParser(inputReader, pipeFormat);
    					} else {
    						throw new KuratorException("Unable to recognize format of provided input file");
    					}
    				}
    				
    				Map<String,Integer> csvHeader = csvParser.getHeaderMap();
    				String[] headers = new String[csvHeader.size()];

    				Iterator<CSVRecord> dataIterator = csvParser.iterator();
    				while (dataIterator.hasNext()) { 
    				   CSVRecord record = dataIterator.next();
    				   if (record.isConsistent()) { 
    					   Map<String,String> recordToStream = new HashMap<String,String>();
    					   Iterator<String> headerIterator = csvHeader.keySet().iterator();
    					   while (headerIterator.hasNext()) {
    						   String header = headerIterator.next();
    						   recordToStream.put(header, record.get(header));
    					   } 
    					   if (recordToStream.size()>0) {
    						   logger.trace(recordToStream.get("occurrenceID") + " " + this.context().self().toString());
    						   broadcast(recordToStream);
    					   } else {
    						   logger.debug("Skipping record with no fields added.");
    					   } 
    					   
    				   } else {
    					   logger.debug("Skipping inconsistent record.");
    				   } 
    				}
    				filesReading.remove(inputfileName);
    			    }
    			} else {
    				logger.error(workspaceName);
    				logger.error(inputfileName);
    				logger.error("Unable to read input file:" + inputfile.getPath());
    				throw new FileNotFoundException("Error: Unable to read upstream file source: " + inputfileName );
    			}
    		} catch (ClassCastException e) { 
    			logger.error("Message was a Map, but unable to cast to Map<String,Object>.");
    			logger.error(e.getMessage());
    		}

    	}
        
    }

}