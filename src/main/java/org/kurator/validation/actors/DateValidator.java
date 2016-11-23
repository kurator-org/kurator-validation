package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.kurator.akka.KuratorActor;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

/**
 * Created by lowery on 11/23/16.
 */
public class DateValidator extends KuratorActor {
    @Override
    protected void onData(Object value) throws Exception {
        Map<String, String> options = (Map<String, String>) value;
        File workspace = new File(options.get("workspace"));
        File outputfile = new File(options.get("outputfile"));

        System.out.println(outputfile);

        for (Map<String, String> record : readFile(outputfile)) {
             System.out.println(record);
        }
    }

    private List<Map<String, String>> readFile(File file) throws Exception {
        FileReader reader = new FileReader(file);

        CSVFormat csvFormat = CSVFormat.TDF.withHeader();

        try (CSVParser csvParser = new CSVParser(reader, csvFormat)) {
            List<Map<String, String>> records = new ArrayList<>();

            Map<String, Integer> csvHeader = csvParser.getHeaderMap();
            String[] headers = new String[csvHeader.size()];
            int i = 0;
            for (String header : csvHeader.keySet()) {
                headers[i++] = header;
            }

            System.out.println(csvHeader);

            for (Iterator<CSVRecord> iterator = csvParser.iterator(); iterator.hasNext(); ) {

                CSVRecord csvRecord = iterator.next();

                if (!csvRecord.isConsistent()) {
                    throw new Exception("Wrong number of fields in record " + csvRecord.getRecordNumber());
                }

                Map<String, String> record = new HashMap<>();

                for (String header : headers) {
                    String value = csvRecord.get(header);
                    record.put(header, value);
                }

                records.add(record);
            }

            return records;
        }
    }
}


