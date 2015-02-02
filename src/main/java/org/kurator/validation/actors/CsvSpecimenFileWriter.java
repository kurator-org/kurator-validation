package org.kurator.validation.actors;

import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

import org.kurator.akka.actors.AkkaActor;
import org.kurator.validation.data.OrderedSpecimenRecord;

import com.csvreader.CsvWriter;

import fp.util.SpecimenRecord;

public class CsvSpecimenFileWriter extends AkkaActor {

    public Writer outputWriter;
    public String filePath = null;
    
    private Boolean headerWritten = false;
    private List<String> headers = new ArrayList<String>();
    private CsvWriter csvWriter;
    
    public void handleStart() throws Exception {
        
        if (outputWriter == null && filePath != null) {
            outputWriter = getFileWriterForPath(filePath);
        }
        
        if (outputWriter == null) {
            throw new Exception("No file or output writer specified for CsVSpecimenFileWriter.");
        }
        
        csvWriter = new CsvWriter(outputWriter, ',');
    }
    
    public void handleEnd() throws Exception {
        csvWriter.close();
    }
    
    @Override
    public void handleData(Object value) throws Exception {

        if (value instanceof SpecimenRecord) {
        
            SpecimenRecord record = (SpecimenRecord) value;
            if (!headerWritten) {
                writeHeaderToFile(record);
                headerWritten = true;
            }
            
            writeRecordValuesToFile(record);
        }
    }

    
    
    private Writer getFileWriterForPath(String path) {
        
        Writer writer = null;
        
        try {        
            writer = new FileWriter(path, false);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
        
        return writer;
    }
    
    private void writeHeaderToFile(SpecimenRecord record) {
        try {

            if (record instanceof OrderedSpecimenRecord) {
                for (String label : ((OrderedSpecimenRecord)record).getKeyList()) {
                    csvWriter.write(label);
                    headers.add(label);
                }
            } else {            
                for (String label : record.keySet()) {
                    csvWriter.write(label);
                    headers.add(label);
                }
            }
            
            csvWriter.endRecord();
            
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }
    
    private void writeRecordValuesToFile(SpecimenRecord record) {
        try {
            
            for (String header : headers) {
                csvWriter.write(record.get(header));
            }
            
            csvWriter.endRecord();
            
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }
}

