from StringUtils import has_content
from StringUtils import SpacedStringBuilder
from DarwinCore import DarwinCore

class SciNameAssembler(object):

    def __init__(
        self,
        genus_field_name                 = DarwinCore.field_names['GENUS'],
        subgenus_field_name              = DarwinCore.field_names['SUBGENUS'],
        specific_epithet_field_name      = DarwinCore.field_names['SPECIFIC_EPITHET'],
        verbatim_taxon_rank_field_name   = DarwinCore.field_names['VERBATIM_TAXON_RANK'],
        taxon_rank_field_name            = DarwinCore.field_names['TAXON_RANK'],
        infraspecific_epithet_field_name = DarwinCore.field_names['INFRASPECIFIC_EPITHET']
    ):
        self._genus_field_name                 = genus_field_name
        self._subgenus_field_name              = subgenus_field_name
        self._specific_epithet_field_name      = specific_epithet_field_name
        self._verbatim_taxon_rank_field_name   = verbatim_taxon_rank_field_name
        self._taxon_rank_field_name            = taxon_rank_field_name
        self._infraspecific_epithet_field_name = infraspecific_epithet_field_name

    def assemble_name(
            self,
            genus,
            subgenus,
            specific_epithet,
            verbatim_taxon_rank,
            taxon_rank,
            infraspecific_epithet
    ):

        if not has_content(genus):
            raise Exception('SciNameAssembler requires value for ' +
                            self._genus_field_name)

        if not has_content(infraspecific_epithet) and not has_content(specific_epithet):
            raise Exception('SciNameAssembler requires values for ' +
                            _specific_epithet_field_name +
                            ' if ' + _infraspecific_epithet_field_name + ' provided')

        return str(SpacedStringBuilder()
                   .append(genus)
                   .append(subgenus)
                   .append(specific_epithet)
                   .append(verbatim_taxon_rank if has_content(verbatim_taxon_rank) else taxon_rank)
                   .append(infraspecific_epithet)
                   )

    def assemble_name(self, record):
        """
        :type record: dict
        """
        return assemble_name(
            record[self._genus_field_name],
            record[self._subgenus_field_name],
            record[self._specific_epithet_field_name],
            record[self._verbatim_taxon_rank_field_name],
            record[self._taxon_rank_field_name],
            record[self._infraspecific_epithet_field_name]
        )
