package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.ffdq.rdf.FFDQModel;
import org.datakurator.ffdq.runner.TestRunner;
import org.datakurator.postprocess.XLSXPostProcessor;
import org.eclipse.rdf4j.rio.RDFFormat;
import org.filteredpush.qc.date.DwCEventDQ;
import org.kurator.akka.KuratorActor;

import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.net.URL;
import java.util.*;

/**
 * Created by lowery on 11/23/16.
 */
public class DateValidator extends KuratorActor {
    private CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();
    private CSVFormat tsvFormat = CSVFormat.newFormat('\t').withHeader();

    public String rdfIn;

    public Integer validationYearLowerBound;

    public Integer whollyOutOfRangeLowerBound;
    public Boolean whollyOutOfRangeUseLowerBound;

    public Integer extendsOutOfRangeLowerBound;
    public Boolean extendsOutOfRangeUseLowerBound;

    @Override
    protected void onData(Object data) throws Exception {
        try {
            // Workflow parameters mapped to test parameters to be used as argument to test runner constructor
            Map<String, Object> params = new HashMap<>();
            params.put("validationYearLowerBound", validationYearLowerBound);

            params.put("whollyOutOfRangeLowerBound", whollyOutOfRangeLowerBound);
            params.put("whollyOutOfRangeUseLowerBound", whollyOutOfRangeUseLowerBound);

            params.put("extendsOutOfRangeLowerBound", extendsOutOfRangeLowerBound);
            params.put("extendsOutOfRangeUseLowerBound", extendsOutOfRangeUseLowerBound);

            Map<String, Object> options = (Map<String, Object>) data;
            File workspace = new File((String) options.get("workspace"));
            File inputfile = new File((String) options.get("outputfile"));

            String reportFile = "dq_report.rdf";
            String xlsxFile = "dq_report.xlsx";

            FileWriter reportWriter = new FileWriter(options.get("workspace") + File.separator + reportFile);
            //List<String> fields = Arrays.asList("dwc:eventDate", "dwc:month", "dwc:day", "dwc:year", "dwc:startDayOfYear",
            //        "dwc:endDayOfYear", "dwc:eventTime", "dwc:verbatimEventDate");

            // Initialize the the ffdq model
            FFDQModel model = new FFDQModel();

            // Load test definitions from rdf file into model
            //if (!rdfFile.exists()) {
            //   throw new FileNotFoundException("RDF input file not found: " + rdfFile.getAbsolutePath());
            //}

            model.load(new URL(rdfIn).openStream(), RDFFormat.TURTLE);

            TestRunner runner = new TestRunner(DwCEventDQ.class, model, params);

            try {
                parseInputfile(runner, inputfile, csvFormat);
            } catch (IllegalArgumentException e) {
                // Try tsv
                logger.debug("File does not appear to be csv, trying tsv format.");
                parseInputfile(runner, inputfile, tsvFormat);
            }

            String reportFileName = options.get("workspace") + File.separator + reportFile;
            OutputStream reportOut = new FileOutputStream(reportFileName);
            model.write(RDFFormat.TURTLE, reportOut);
            reportOut.close();

            //String reportXlsFile = "dq_report.xls";
            //File reportXls = new File(options.get("workspace") + File.separator + reportXlsFile);

            //InputStream config = DateValidator.class.getResourceAsStream("/ffdq-assertions.json");
            //FFDQPostProcessor postProcessor = new FFDQPostProcessor(summary, config);
            //postProcessor.reportSummary(reportXls);


            Map<String, String> artifacts = (Map<String, String>) options.get("artifacts");

            publishArtifact("dq_report_file", reportFileName);
            artifacts.put("dq_report_file", reportFileName);

            // Postprocessor
            String xlsxFileName = options.get("workspace") + File.separator + xlsxFile;
            XLSXPostProcessor postProcessor = new XLSXPostProcessor(model);
            postProcessor.postprocess(new FileOutputStream(xlsxFileName));

            publishArtifact("dq_report_xls_file", xlsxFileName);
            artifacts.put("dq_report_xls_file", xlsxFileName);

            //artifactFileName = options.get("workspace") + File.separator + outputfile;
            //publishArtifact("event_dates_file", artifactFileName);
            //artifacts.put("event_dates_file", artifactFileName);

            //artifactFileName = options.get("workspace") + File.separator + reportXlsFile;
            //publishArtifact("dq_report_xls_file", artifactFileName);
            //artifacts.put("dq_report_xls_file", artifactFileName);
            System.out.println("Options: " + options);

            broadcast(options);
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }
    }

    private void parseInputfile(TestRunner runner, File inputfile, CSVFormat format) throws IOException, IllegalAccessException, InvocationTargetException, InstantiationException, IllegalArgumentException {
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

                logger.info(record.toString());
                runner.run(record);
            }
        }
    }
}


