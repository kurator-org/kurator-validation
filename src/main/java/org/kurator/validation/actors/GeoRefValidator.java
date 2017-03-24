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
import org.datakurator.postprocess.xlsx.DQReportParser;
import org.datakurator.postprocess.xlsx.XLSXPostProcessor;
import org.filteredpush.qc.date.DwCEventDQ;
import org.filteredpush.qc.georeference.DwCGeoRefDQ;
import org.kurator.akka.KuratorActor;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.util.*;

/**
 * Created by lowery on 11/23/16.
 */
public class GeoRefValidator extends KuratorActor {
    private CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();
    private CSVFormat tsvFormat = CSVFormat.TDF.withHeader();

    @Override
    protected void onData(Object data) throws Exception {
        Map<String, Object> options = (Map<String, Object>) data;
        File workspace = new File((String) options.get("workspace"));
        File inputfile = new File((String) options.get("outputfile"));

        String reportFile = "dq_report.json";
        String xlsxFile = "dq_report.xlsx";

        FileWriter reportWriter = new FileWriter(options.get("workspace") + File.separator + reportFile);

        ValidationRunner runner = new ValidationRunner(DwCGeoRefDQ.class, reportWriter);

        try {
            parseInputfile(runner, inputfile, csvFormat);
        } catch (IllegalArgumentException e) {
            // Try tsv
            logger.debug("File does not appear to be csv, trying tsv format.");
            parseInputfile(runner, inputfile, tsvFormat);
        }

        Map<String, String> artifacts = (Map<String, String>) options.get("artifacts");

        String reportFileName = options.get("workspace") + File.separator + reportFile;
        publishArtifact("dq_report_file", reportFileName, "DQ_REPORT");
        artifacts.put("dq_report_file", reportFileName);

        // Postprocessor
        String xlsxFileName = options.get("workspace") + File.separator + xlsxFile;
        XLSXPostProcessor postProcessor = new XLSXPostProcessor(new FileInputStream(reportFileName));
        postProcessor.postprocess(new FileOutputStream(xlsxFileName));

        publishArtifact("dq_report_xls_file", xlsxFileName);
        artifacts.put("dq_report_xls_file", xlsxFileName);

        broadcast(options);
    }

    private void parseInputfile(ValidationRunner runner, File inputfile, CSVFormat format) throws IOException, IllegalAccessException, InvocationTargetException, InstantiationException, IllegalArgumentException {
        FileReader reader = new FileReader(inputfile);

        try (CSVParser csvParser = new CSVParser(reader, format)) {
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
                    throw new IllegalArgumentException("Wrong number of fields in record " + csvRecord.getRecordNumber());
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


