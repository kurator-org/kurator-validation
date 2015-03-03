package org.kurator.validation.actors;

import java.util.Map;

import org.kurator.akka.data.SpacedStringBuilder;
import org.kurator.akka.data.Util;
import org.kurator.validation.exceptions.MissingFieldException;
import org.kurator.validation.standards.DarwinCore;

public class SciNameAssembler {

    public final String GENUS_FIELD_NAME;
    public final String SUBGENUS_FIELD_NAME;
    public final String SPECIFIC_EPITHET_FIELD_NAME;
    public final String VERBATIM_TAXON_RANK_FIELD_NAME;
    public final String TAXON_RANK_FIELD_NAME;
    public final String INFRASPECIFIC_EPITHET_FIELD_NAME;

    public SciNameAssembler(
            String genusFieldName, 
            String subgenusFieldName,
            String specificEpithetFieldName, 
            String verbatimTaxonRankFieldName,
            String taxonRankFieldName, 
            String infraspecificEpithetFieldName
    ) {
        GENUS_FIELD_NAME                 = genusFieldName;
        SUBGENUS_FIELD_NAME              = subgenusFieldName;
        SPECIFIC_EPITHET_FIELD_NAME      = specificEpithetFieldName;
        VERBATIM_TAXON_RANK_FIELD_NAME   = verbatimTaxonRankFieldName;
        TAXON_RANK_FIELD_NAME            = taxonRankFieldName;
        INFRASPECIFIC_EPITHET_FIELD_NAME = infraspecificEpithetFieldName;
    }

    public static SciNameAssembler newDwCSciNameAssembler() {
        return new SciNameAssembler(
                DarwinCore.FieldNames.GENUS,
                DarwinCore.FieldNames.SUBGENUS,
                DarwinCore.FieldNames.SPECIFIC_EPITHET,
                DarwinCore.FieldNames.VERBATIM_TAXON_RANK,
                DarwinCore.FieldNames.TAXON_RANK,
                DarwinCore.FieldNames.INFRASPECIFIC_EPITHET);
    }

    public String assembleName(Map<String, String> record) throws Exception {

        return assembleName(
                record.get(GENUS_FIELD_NAME),
                record.get(SUBGENUS_FIELD_NAME),
                record.get(SPECIFIC_EPITHET_FIELD_NAME),
                record.get(VERBATIM_TAXON_RANK_FIELD_NAME),
                record.get(TAXON_RANK_FIELD_NAME),
                record.get(INFRASPECIFIC_EPITHET_FIELD_NAME)
        );
    }

    public String assembleName(
            String genus, 
            String subgenus,
            String specificEpithet, 
            String verbatimTaxonRank, 
            String taxonRank,
            String infraspecificEpithet
    ) throws Exception {

        if (!Util.hasContent(genus)) {
            throw new MissingFieldException(
                "SciNameAssembler",
                GENUS_FIELD_NAME
            );
        }

        if (Util.hasContent(infraspecificEpithet)
                && !Util.hasContent(specificEpithet)) {
            throw new MissingFieldException("SciNameAssembler",
                    SPECIFIC_EPITHET_FIELD_NAME, 
                    "if " + INFRASPECIFIC_EPITHET_FIELD_NAME + " provided"
            );
        }

        return new SpacedStringBuilder()
                .append(genus)
                .append(subgenus)
                .append(specificEpithet)
                .append(Util.hasContent(verbatimTaxonRank) ? verbatimTaxonRank : taxonRank)
                .append(infraspecificEpithet)
                .toString();
    }
}
