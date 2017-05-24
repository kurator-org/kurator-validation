/** WorkspaceCsvFileWriter.java
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

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.kurator.akka.KuratorActor;
import org.kurator.akka.messages.EndOfStream;
import org.python.core.PyNone;

/**
 * A workspace aware CSV file writer.  Takes the file name/path below the workspace as a parameter and
 * can extract workspace name/path from a dictionary message.
 * 
 * @author mole
 *
 */
public class WorkspaceCsvFileWriter extends KuratorActor {

    private String filePath = null;
    private boolean quoteValuesContainingDelimiter = true;
    private boolean quoteAllValues = false;
    private String recordSeparator = System.getProperty("line.separator");
    private boolean trimValues = false;
    private boolean showHeader = false;
    private char quoteCharacter = '"';
    private char fieldDelimiter = ',';
    private String[] headers = null;
    
    protected Writer outputWriter = null;
    protected CSVPrinter csvPrinter = null;
    
    /**
     * Number of streams to which this actor listens.
     */
    private int listensTo = 1;
    /**
     * Number of end of stream messages that have been received.
     */
    private int eosHeard = 0;
    
	public void setNumberOfInputs(int numberOfInputs) { 
		listensTo = numberOfInputs;
	}    
    
    /**
	 * @return the outputWriter
	 */
	public Writer getOutputWriter() {
		return outputWriter;
	}

	/**
	 * @param outputWriter the outputWriter to set
	 */
	public void setOutputWriter(Writer outputWriter) {
		this.outputWriter = outputWriter;
	}

	/**
	 * @return the filePath
	 */
	public String getFilePath() {
		return filePath;
	}

	/**
	 * @param filePath the filePath to set
	 */
	public void setFilePath(String filePath) {
		this.filePath = filePath;
	}

	/**
	 * @return the quoteValuesContainingDelimiter
	 */
	public boolean isQuoteValuesContainingDelimiter() {
		return quoteValuesContainingDelimiter;
	}

	/**
	 * @param quoteValuesContainingDelimiter the quoteValuesContainingDelimiter to set
	 */
	public void setQuoteValuesContainingDelimiter(
			boolean quoteValuesContainingDelimiter) {
		this.quoteValuesContainingDelimiter = quoteValuesContainingDelimiter;
	}

	/**
	 * @return the quoteAllValues
	 */
	public boolean isQuoteAllValues() {
		return quoteAllValues;
	}

	/**
	 * @param quoteAllValues the quoteAllValues to set
	 */
	public void setQuoteAllValues(boolean quoteAllValues) {
		this.quoteAllValues = quoteAllValues;
	}

	/**
	 * @return the recordSeparator
	 */
	public String getRecordSeparator() {
		return recordSeparator;
	}

	/**
	 * @param recordSeparator the recordSeparator to set
	 */
	public void setRecordSeparator(String recordSeparator) {
		this.recordSeparator = recordSeparator;
	}

	/**
	 * @return the trimValues
	 */
	public boolean isTrimValues() {
		return trimValues;
	}

	/**
	 * @param trimValues the trimValues to set
	 */
	public void setTrimValues(boolean trimValues) {
		this.trimValues = trimValues;
	}

	/**
	 * @return the showHeader
	 */
	public boolean isShowHeader() {
		return showHeader;
	}

	/**
	 * @param showHeader the showHeader to set
	 */
	public void setShowHeader(boolean showHeader) {
		this.showHeader = showHeader;
	}

	/**
	 * @return the quoteCharacter
	 */
	public char getQuoteCharacter() {
		return quoteCharacter;
	}

	/**
	 * @param quoteCharacter the quoteCharacter to set
	 */
	public void setQuoteCharacter(char quoteCharacter) {
		this.quoteCharacter = quoteCharacter;
	}

	/**
	 * @return the fieldDelimiter
	 */
	public char getFieldDelimiter() {
		return fieldDelimiter;
	}

	/**
	 * @param fieldDelimiter the fieldDelimiter to set
	 */
	public void setFieldDelimiter(char fieldDelimiter) {
		this.fieldDelimiter = fieldDelimiter;
	}

	/**
	 * @return the headers
	 */
	public String[] getHeaders() {
		return headers;
	}

	/**
	 * @param headers the headers to set
	 */
	public void setHeaders(String[] headers) {
		this.headers = headers;
	}

	@Override
    public void onStart() throws Exception {
    	if (outputWriter == null) {
    		if (filePath == null) {
    			outputWriter = new OutputStreamWriter(outStream);
    		}
    	}
    }

    @Override
    public void onData(Object data) throws Exception {

        if (data instanceof Map<?,?>) {

        	boolean messageSetWorkspace = false;
        	
    		@SuppressWarnings("unchecked")
    		Map<String, Object> options = null;
    		try { 
    			options = (Map<String, Object>) data;
    			String workspaceName = (String) options.get("workspace");
    			if (workspaceName !=null) { 
    				if (outputWriter == null) {
    					if (filePath != null) {
    						String filename = workspaceName + File.separator + filePath;
    						logger.debug("OutputFile:" + filename);
    						outputWriter = new FileWriter(filename, false);
    					} else {
    						outputWriter = new OutputStreamWriter(outStream);
    					}
    					logger.trace("OutputWriter: " + outputWriter.toString());
    				    messageSetWorkspace = true;	
    				}
    			}
    		} catch (ClassCastException e) { 
    			logger.debug(e.getMessage());
    		}
        	
    		if (!messageSetWorkspace) {
    			// print data
    			@SuppressWarnings("unchecked")
    			Map<String,Object> record = (Map<String,Object>) data;
            
    			if (csvPrinter == null) {
    				if (headers== null) {
    					buildHeader(record);
    					logger.debug(headers.toString());
    				}
    				createCsvPrinter();
    			}

    			for (Map.Entry<String, Object> entry : record.entrySet()) {
    				if(entry.getValue() instanceof PyNone) {
    					entry.setValue(null);
    				}
    			}
            
            csvPrinter.printRecord(record.values());
    		}
        }
    }

	/**
	 * Implementation of onEndOfStream that waits for all input streams to send 
	 * end of stream messages before triggering end of stream and stop.
	 * Assumes message delivery model of at most once.
	 * 
	 * @param eos end of stream signal.
	 */
    @Override
    protected void onEndOfStream(EndOfStream eos) throws Exception {
        logger.trace("WorkspaceCsvFileWriter ON_END_OF_STREAM_EVENT ("+ eosHeard + " of " + listensTo +") heard.");
        if (endOnEos && eosHeard>=listensTo) {
        	logger.trace("WorkspaceCsvFileWriter ON_END_OF_STREAM_EVENT handler invoked.");
            endStreamAndStop(eos);
        } else { 
        	eosHeard++;
        }
    }	
    
    
    @Override
    public void onEnd() throws Exception {
        if (csvPrinter != null) {
            csvPrinter.close();
        }
    }
    
    private void createCsvPrinter() throws IOException {
        
        QuoteMode quoteModePolicy;
        if (quoteAllValues) {
            quoteModePolicy = QuoteMode.ALL;
        } else if (quoteValuesContainingDelimiter) {
            quoteModePolicy = QuoteMode.MINIMAL;
        } else {
            quoteModePolicy = QuoteMode.NONE;
        }
            
        CSVFormat csvFormat = CSVFormat.newFormat(fieldDelimiter)
                .withQuoteMode(quoteModePolicy)
                .withQuote(quoteCharacter)
                .withRecordSeparator(recordSeparator)
                .withSkipHeaderRecord(!showHeader)
                .withHeader(headers);
        
        csvPrinter = new CSVPrinter(outputWriter, csvFormat);
        logger.debug(csvPrinter.toString());
    }
    
    private void buildHeader(Map<String,Object> record) {
        headers = new String[record.size()];
        int i = 0;
        for (String label : record.keySet()) {
            headers[i++] = label;
        }
    }
}
