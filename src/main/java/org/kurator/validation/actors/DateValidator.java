package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.data.ffdq.DQReport;
import org.datakurator.data.ffdq.DQReportBuilder;
import org.datakurator.data.ffdq.runner.ValidationRunner;
import org.datakurator.data.provenance.BaseRecord;
import org.datakurator.postprocess.FFDQPostProcessor;
import org.filteredpush.qc.date.DwCEventDQ;
import org.kurator.akka.KuratorActor;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.util.*;

/**
 * Created by lowery on 11/23/16.
 */
public class DateValidator extends KuratorActor {
    private CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();

    @Override
    protected void onData(Object data) throws Exception {
        Map<String, Object> options = (Map<String, Object>) data;
        File workspace = new File((String) options.get("workspace"));
        File inputfile = new File((String) options.get("outputfile"));

        String reportFile = "dq_report.json";

        FileWriter reportWriter = new FileWriter(options.get("workspace") + File.separator + reportFile);
        //List<String> fields = Arrays.asList("dwc:eventDate", "dwc:month", "dwc:day", "dwc:year", "dwc:startDayOfYear",
        //        "dwc:endDayOfYear", "dwc:eventTime", "dwc:verbatimEventDate");

        ValidationRunner runner = new ValidationRunner(DwCEventDQ.class, reportWriter);

        FileReader reader = new FileReader(inputfile);

        try (CSVParser csvParser = new CSVParser(reader, csvFormat)) {
            List<Map<String, String>> records = new ArrayList<>();

            Map<String, Integer> csvHeader = csvParser.getHeaderMap();
            String[] headers = new String[csvHeader.size()];
            int i = 0;
            for (String header : csvHeader.keySet()) {
                headers[i++] = header;
            }

            reportWriter.write('[');

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

                if (iterator.hasNext()) {
                    reportWriter.write(",");
                }
            }

            reportWriter.write(']');
            reportWriter.close();
        }


        //String reportXlsFile = "dq_report.xls";
        //File reportXls = new File(options.get("workspace") + File.separator + reportXlsFile);

        // Postprocessor
        //InputStream config = DateValidator.class.getResourceAsStream("/ffdq-assertions.json");
        //FFDQPostProcessor postProcessor = new FFDQPostProcessor(summary, config);
        //postProcessor.reportSummary(reportXls);

        Map<String, String> artifacts = (Map<String, String>) options.get("artifacts");

        String artifactFileName = options.get("workspace") + File.separator + reportFile;
        publishArtifact("dq_report_file", artifactFileName, "DQ_REPORT");
        artifacts.put("dq_report_file", artifactFileName);

        //artifactFileName = options.get("workspace") + File.separator + outputfile;
        //publishArtifact("event_dates_file", artifactFileName);
        //artifacts.put("event_dates_file", artifactFileName);

        //artifactFileName = options.get("workspace") + File.separator + reportXlsFile;
        //publishArtifact("dq_report_xls_file", artifactFileName);
        //artifacts.put("dq_report_xls_file", artifactFileName);

        broadcast(options);
    }

    private DQReport createReport(BaseRecord result) throws IOException {
        InputStream config = DateValidator.class.getResourceAsStream("/ffdq-assertions.json");
        DQReportBuilder builder = new DQReportBuilder(config);

        DQReport report = builder.createReport(result);

        return report;
    }
}


