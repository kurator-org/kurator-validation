package org.kurator.validation.actors;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;

import org.kurator.akka.KuratorAkkaCLI;
import org.kurator.akka.KuratorAkkaTestCase;
import org.kurator.akka.WorkflowRunner;
import org.kurator.akka.YamlFileWorkflowRunner;

public class TestWoRMSNameValidation extends KuratorAkkaTestCase {

    static final String RESOURCE_PATH = "classpath:/org/kurator/validation/workflows/";

    private OutputStream outputBuffer;
    private Writer bufferWriter;

    @Override
    public void setUp() throws Exception {
        super.setUp();
        KuratorAkkaCLI.enableLog4J();

        outputBuffer = new ByteArrayOutputStream();
        bufferWriter = new OutputStreamWriter(outputBuffer);
    }

    public void testWoRMSNameValidation() throws Exception {

        WorkflowRunner wr = new YamlFileWorkflowRunner(RESOURCE_PATH + "WoRMS_name_validation.yaml");
        wr.apply("in", "src/test/resources/org/kurator/validation/data/testinput_moll.csv");
        wr.apply("writer", bufferWriter);
        wr.apply("FileWriter.quoteCharacter", '\'');
        wr.build();
        wr.run();

        String expected =
            "ID,TaxonName,Author,OriginalName,OriginalAuthor,lsid" + EOL +
            "37929,Architectonica reevei,'(Hanley, 1862)',Architectonica reevi,,urn:lsid:marinespecies.org:taxname:588206" + EOL +
            "37932,Rapana rapiformis,'(Born, 1778)',Rapana rapiformis,'(Von Born, 1778)',urn:lsid:marinespecies.org:taxname:140415" + EOL +
            "180593,Buccinum donomani,'(Linnaeus, 1758)',,," + EOL +
            "179963,Codakia paytenorum,'(Iredale, 1937)',Codakia paytenorum,'Iredale, 1937',urn:lsid:marinespecies.org:taxname:215841" + EOL +
            "0,Rissoa venusta,'Garrett, 1873',Rissoa venusta,,urn:lsid:marinespecies.org:taxname:607233" + EOL +
            "62156,Rissoa venusta,'Garrett, 1873',Rissoa venusta,Phil.,urn:lsid:marinespecies.org:taxname:607233" + EOL;

        assertEquals(expected, outputBuffer.toString());
    }
}