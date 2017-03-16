package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.data.ffdq.runner.ValidationRunner;
import org.filteredpush.qc.date.DwCEventDQ;
import org.filteredpush.qc.georeference.DwCGeoRefDQ;

import java.io.*;
import java.util.*;

/**
 * Created by lowery on 3/15/17.
 */
public class GeoRefValidator {
    private static CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();

    public static void main(String [] args) throws Exception {
        FileWriter reportWriter = new FileWriter("georef.json");

        ValidationRunner runner = new ValidationRunner(DwCEventDQ.class, reportWriter);

        FileReader reader = new FileReader(args[0]);

        try (CSVParser csvParser = new CSVParser(reader, csvFormat)) {
            Map<String, Integer> csvHeader = csvParser.getHeaderMap();
            String[] headers = new String[csvHeader.size()];
            int i = 0;
            for (String header : csvHeader.keySet()) {
                headers[i++] = header;
            }

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

                runner.validate(record);
            }

            runner.close();
        }
    }
}
