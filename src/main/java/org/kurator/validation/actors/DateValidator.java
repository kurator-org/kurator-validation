package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.data.ffdq.DQReport;
import org.datakurator.data.ffdq.DQReportBuilder;
import org.datakurator.data.ffdq.runner.ValidationRunner;
import org.datakurator.data.provenance.BaseRecord;
import org.filteredpush.kuration.data.DateFragment;
import org.kurator.akka.KuratorActor;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.util.*;

/**
 * Created by lowery on 11/23/16.
 */
public class DateValidator extends KuratorActor {
    private CSVFormat csvFormat = CSVFormat.TDF.withHeader();

    @Override
    protected void onData(Object value) throws Exception {
        Map<String, Object> options = (Map<String, Object>) value;
        File workspace = new File((String) options.get("workspace"));
        File inputfile = new File((String) options.get("outputfile"));

        String outputfile = "event_dates.tsv";

        List<DQReport> summary = new ArrayList<>();

        FileWriter writer = new FileWriter(workspace + File.separator + "event_dates.tsv");
        CSVPrinter csvPrinter = new CSVPrinter(writer, csvFormat.withHeader("initialValue", "curatedValue", "year",
                "month", "day", "verbatimEventDate", "status"));

        for (Map<String, String> record : readFile(inputfile)) {
            validate(record);

            BaseRecord result = org.filteredpush.kuration.validators.DateValidator.validateEventConsistencyWithContext(record.get("id"),
                    record.get("eventDate"), record.get("year"), record.get("month"), record.get("day"),
                    record.get("startDayOfYear"), record.get("endDayOfYear"), record.get("eventTime"),
                    record.get("verbatimEventDate"));

            csvPrinter.printRecord(record.get("eventDate"), result.get("eventDate"), result.get("year"),
                    result.get("month"), result.get("day"), result.get("verbatimEventDate"),
                    result.getCurationStatus("eventDate"));

            DQReport report = createReport(result);
            summary.add(report);
        }

        csvPrinter.close();

        String reportFile = "dq_report.json";
        FileWriter reportWriter = new FileWriter(options.get("workspace") + File.separator + reportFile);

        StringWriter strWriter = new StringWriter();
        int count = 0;
        strWriter.write('[');
        for (DQReport report : summary) {
            report.write(strWriter);
            if (count++ < summary.size()-1) {
                strWriter.write(",");
            }
        }
        strWriter.write(']');

        reportWriter.write(strWriter.toString());
        reportWriter.close();

        Map<String, String> artifacts = (Map<String, String>) options.get("artifacts");

        String artifactFileName = options.get("workspace") + File.separator + reportFile;
        publishArtifact("dq_report_file", artifactFileName, "DQ_REPORT");
        artifacts.put("dq_report_file", artifactFileName);

        artifactFileName = options.get("workspace") + File.separator + outputfile;
        publishArtifact("event_dates_file", artifactFileName);
        artifacts.put("event_dates_file", artifactFileName);

        broadcast(options);
    }

    private void validate(Map<String, String> record) {
        /*try {
            ValidationRunner runner = new ValidationRunner(DateUtils.class);
            runner.validate(record);
        } catch (Exception e) {
            e.printStackTrace();
        }*/
    }

    private DQReport createReport(BaseRecord result) throws IOException {
        InputStream config = DateValidator.class.getResourceAsStream("/ffdq-assertions.json");
        DQReportBuilder builder = new DQReportBuilder(config);

        DQReport report = builder.createReport(result);

        return report;
    }

    private List<Map<String, String>> readFile(File file) throws Exception {
        FileReader reader = new FileReader(file);

        try (CSVParser csvParser = new CSVParser(reader, csvFormat)) {
            List<Map<String, String>> records = new ArrayList<>();

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

                records.add(record);
            }

            return records;
        }
    }
}


