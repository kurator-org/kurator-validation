package org.kurator.validation.actors;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.datakurator.data.ffdq.runner.ValidationRunner;
import org.filteredpush.qc.georeference.GeoTester;
import org.filteredpush.qc.georeference.util.GEOUtil;
import org.joda.time.format.ISODateTimeFormat;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;

public class GeoreferenceChecker {
    private static CSVFormat csvFormat = CSVFormat.DEFAULT.withHeader();
    private static CSVFormat tsvFormat = CSVFormat.TDF.withHeader();


    private ExecutorService executor = Executors.newFixedThreadPool(8);
    private GeoTester tester;

    private int count = 0;
    private long startTime;

    public GeoreferenceChecker() throws IOException {
        tester = new GeoTester();
    }


    public static void main(String[] args) throws IOException, IllegalAccessException, InstantiationException, InvocationTargetException {
        GeoreferenceChecker georeferenceChecker = new GeoreferenceChecker();
        georeferenceChecker.parseCSV(new File("/home/lowery/IdeaProjects/kurator-validation/src/test/resources/org/kurator/validation/data/arctos.csv"), csvFormat);
    }

    public void parseCSV(File inputfile, CSVFormat format) throws IOException, IllegalAccessException, InvocationTargetException, InstantiationException, IllegalArgumentException {
        String start = ISODateTimeFormat.dateHourMinuteSecond().print(new Date().getTime());
        FileReader reader = new FileReader(inputfile);

        try (CSVParser csvParser = new CSVParser(reader, format)) {

            Map<String, Integer> csvHeader = csvParser.getHeaderMap();
            String[] headers = new String[csvHeader.size()];
            int i = 0;
            for (String header : csvHeader.keySet()) {
                headers[i++] = header;
            }

            startTime = System.currentTimeMillis();

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

                //executor.execute(() -> {
                //    try {

                tester.validate(record);
                count++;

                //        if (count % 1000 == 0) {
                //            System.out.println("processed " + count + " records, " + (System.currentTimeMillis() - startTime));
                //            startTime = System.currentTimeMillis();
                //        }
                //    } catch (IOException e) {
                //        e.printStackTrace();
                //    }
                //});

            }
        }

        //executor.execute(() -> {
        //    String end = ISODateTimeFormat.dateHourMinuteSecond().print(new Date().getTime());
        //    System.out.println();
        //    System.out.println("STARTED: " + start);
        //    System.out.println("ENDED: " + end);
        //});

        //executor.shutdown();
        tester.close();
    }

}
