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
    
    private final String WORKFLOW_RESOURCE_PATH="src/main/python/kurator/validation/workflows";
    
    @Override
    public void setUp() throws Exception {
        super.setUp();
        KuratorAkkaCLI.enableLog4J();
        outputBuffer = new ByteArrayOutputStream();
        outPrintStream = new PrintStream(outputBuffer);
    }

    public void testWoRMSNameValidation() throws Exception {

        WorkflowRunner wr = new YamlFileWorkflowRunner("file:" + WORKFLOW_RESOURCE_PATH + "/WoRMS_name_validation.yaml");
        wr.outputStream(outPrintStream);
        wr.apply("ReadInput.filePath", WORKFLOW_RESOURCE_PATH + "/WoRMS_name_validation_input.csv");
        wr.apply("WriteOutput.quoteCharacter", '\'');
        wr.build();
        wr.run();

        String expected =
            "ID,TaxonName,Author,OriginalName,OriginalAuthor,WoRMsExactMatch,lsid" + EOL +
            "37929,Architectonica reevei,'(Hanley, 1862)',Architectonica reevi,,false,urn:lsid:marinespecies.org:taxname:588206" + EOL +
            "37932,Rapana rapiformis,'(Born, 1778)',Rapana rapiformis,'(Von Born, 1778)',true,urn:lsid:marinespecies.org:taxname:140415" + EOL +
            "180593,Buccinum donomani,'(Linnaeus, 1758)',,,," + EOL +
            "179963,Codakia paytenorum,'(Iredale, 1937)',Codakia paytenorum,'Iredale, 1937',true,urn:lsid:marinespecies.org:taxname:215841" + EOL +
            "0,Rissoa venusta,'Garrett, 1873',Rissoa venusta,,true,urn:lsid:marinespecies.org:taxname:607233" + EOL +
            "62156,Rissoa venusta,'Garrett, 1873',Rissoa venusta,Phil.,true,urn:lsid:marinespecies.org:taxname:607233" + EOL;

        assertEquals(expected, outputBuffer.toString());
    }
}