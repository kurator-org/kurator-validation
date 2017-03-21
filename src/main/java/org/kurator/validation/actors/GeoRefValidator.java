package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.data.ffdq.runner.ValidationRunner;
import org.filteredpush.qc.date.DwCEventDQ;
import org.filteredpush.qc.georeference.DwCGeoRefDQ;
import org.kurator.akka.KuratorActor;

import java.io.*;
import java.util.*;

/**
 * Created by lowery on 3/15/17.
 */
public class GeoRefValidator extends KuratorActor {
    private static CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();

    @Override
    protected void onData(Object data) throws Exception {
        Map<String, Object> options = (Map<String, Object>) data;
        File workspace = new File((String) options.get("workspace"));
        File inputfile = new File((String) options.get("outputfile"));

        String reportFile = "dq_report.json";

        FileWriter reportWriter = new FileWriter(options.get("workspace") + File.separator + reportFile);

        ValidationRunner runner = new ValidationRunner(DwCGeoRefDQ.class, reportWriter);

        FileReader reader = new FileReader(inputfile);

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

        Map<String, String> artifacts = (Map<String, String>) options.get("artifacts");

        String artifactFileName = options.get("workspace") + File.separator + reportFile;
        publishArtifact("dq_report_file", artifactFileName, "DQ_REPORT");
        artifacts.put("dq_report_file", artifactFileName);

        broadcast(options);
    }
}
