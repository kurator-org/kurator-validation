package org.kurator.validation.actors;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.io.PrintStream;

import org.kurator.akka.KuratorAkkaCLI;
import org.kurator.akka.KuratorAkkaTestCase;
import org.kurator.akka.WorkflowRunner;
import org.kurator.akka.YamlFileWorkflowRunner;

public class TestWoRMSNameValidation extends KuratorAkkaTestCase {

    private OutputStream outputBuffer;
    PrintStream outPrintStream;
    
    private final String KURATOR_WORMS_PACKAGE_DIR="packages/kurator_worms/";
    
    @Override
    public void setUp() throws Exception {
        super.setUp();
        KuratorAkkaCLI.enableLog4J();
        outputBuffer = new ByteArrayOutputStream();
        outPrintStream = new PrintStream(outputBuffer);
    }

    public void testWoRMSNameValidation() throws Exception {

        WorkflowRunner wr = new YamlFileWorkflowRunner("file:" + KURATOR_WORMS_PACKAGE_DIR + "workflows/curate_csv_with_worms.yaml");
        wr.outputStream(outPrintStream);
        wr.apply("input", KURATOR_WORMS_PACKAGE_DIR + "data/five_records.csv");
        wr.apply("CleanRecords.fuzzy_match_enabled", "False");
        wr.run();

        String expected =
            "ID,TaxonName,Author,OriginalTaxonName,OriginalAuthor,WoRMSMatchType,LSID"                                                  + EOL +
            "37929,Architectonica reevei,'(Hanley, 1862)',Architectonica reevi,,fuzzy match,urn:lsid:marinespecies.org:taxname:588206"  + EOL +
            "37932,Rapana rapiformis,'(Born, 1778)',Rapana rapiformis,,exact match,urn:lsid:marinespecies.org:taxname:140415"           + EOL +
            "180593,Buccinum donomani,'(Linnaeus, 1758)',,,no match,"                                                                   + EOL +
            "179963,Codakia paytenorum,'(Iredale, 1937)',Codakia paytenorum,,exact match,urn:lsid:marinespecies.org:taxname:215841"     + EOL +
            "62156,Rissoa venusta,Phil.,,,no match,"                                                                                    + EOL;

        assertEquals(expected, outputBuffer.toString());
    }    
 }