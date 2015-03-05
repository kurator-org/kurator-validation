package org.kurator.validation.actors;

import org.kurator.akka.KuratorAkkaTestCase;
import org.kurator.akka.data.GenericMapRecord;

public class TestSciNameAssembler extends KuratorAkkaTestCase {

	SciNameAssembler sciNameAssembler;

	@Override
	public void setUp() {
		sciNameAssembler = SciNameAssembler.newDwCSciNameAssembler();
	}

    public void testSciNameAssembler_EmptyRecord() throws Exception {

    	Exception caught = null;
    	try {
    		sciNameAssembler.assembleName(new GenericMapRecord(new String[] {}));
			fail("Exception expected");
    	} catch (Exception ex) {
    		caught = ex;
    	}
    	assertNotNull(caught);
		assertEquals("SciNameAssembler requires value for genus", caught.getMessage());
    }

	public void testSciNameAssembler_Genus() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", "Emoia"
		}));

		assertEquals("Emoia", assembledName);
    }

	public void testSciNameAssembler_Subgenus() throws Exception {

    	Exception caught = null;
    	try {
    		sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"subgenus", "pallidiceps"
			}));
			fail("Exception expected");
    	} catch (Exception ex) {
    		caught = ex;
    	}
    	assertNotNull(caught);
		assertEquals("SciNameAssembler requires value for genus", caught.getMessage());
    }

    public void testSciNameAssembler_Genus_SpecificEpithet() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 			"Emoia",
				"specificEpithet", 	"pallidiceps"
		}));

		assertEquals("Emoia pallidiceps", assembledName);
    }

    public void testSciNameAssembler_Genus_SpecificEpithet_IntraspecificEpithet() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Hadrurus",
				"specificEpithet", 		"arizonensis",
				"infraspecificEpithet", "arizonensis"
		}));

		assertEquals("Hadrurus arizonensis arizonensis", assembledName);
    }

    public void testSciNameAssembler_Genus_InfraspecificEpithet() throws Exception {

    	Exception caught = null;
    	try {
    		sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Hadrurus",
				"infraspecificEpithet", "arizonensis"
			}));
			fail("Exception expected");
    	} catch (Exception ex) {
    		caught = ex;
    	}
    	assertNotNull(caught);
		assertEquals("SciNameAssembler requires value for specificEpithet if infraspecificEpithet provided", caught.getMessage());
    }

    public void testSciNameAssembler_Genus_SpecificEpithet_IntraspecificEpithet_TaxonRank() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Lithobius",
				"specificEpithet", 		"utahensis",
				"taxonRank",			"var.",
				"infraspecificEpithet", "tiganus"
		}));

		assertEquals("Lithobius utahensis var. tiganus", assembledName);
    }

    public void testSciNameAssembler_Genus_SpecificEpithet_IntraspecificEpithet_VerbatimTaxonRank() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Lithobius",
				"specificEpithet", 		"utahensis",
				"verbatimTaxonRank",	"var.",
				"infraspecificEpithet", "tiganus"
		}));

		assertEquals("Lithobius utahensis var. tiganus", assembledName);
    }

    public void testSciNameAssembler_Genus_SpecificEpithet_IntraspecificEpithet_TaxonRank_Equals_VerbatimTaxonRank() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Lithobius",
				"specificEpithet", 		"utahensis",
				"verbatimTaxonRank",	"var.",
				"taxonRank",			"var.",
				"infraspecificEpithet", "tiganus"
		}));

		assertEquals("Lithobius utahensis var. tiganus", assembledName);
    }

    public void testSciNameAssembler_Genus_SpecificEpithet_IntraspecificEpithet_TaxonRank_DiffersFrom_VerbatimTaxonRank() throws Exception {

		String assembledName = sciNameAssembler.assembleName(new GenericMapRecord(new String[] {
				"genus", 				"Lithobius",
				"specificEpithet", 		"utahensis",
				"verbatimTaxonRank",	"var.verbatim",
				"taxonRank",			"var.",
				"infraspecificEpithet", "tiganus"
		}));

		assertEquals("Lithobius utahensis var.verbatim tiganus", assembledName);
    }
}
