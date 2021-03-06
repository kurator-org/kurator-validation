
from kurator_worms.service import WoRMSService

class RecordCurator(object):
    """
    Actor for curating specimen records using the WoRMS taxonomic name database via the AphiaNameService.
    """

    def __init__(self):
        """ Initialize the WoRMS service client """
        self._worms = WoRMSService()

    def clean_record(self, inputs):

        input_record                = inputs.get('input_record')
        taxon_name_field            = inputs.get('taxon_name_field')
        author_field                = inputs.get('author_field')
        original_taxon_name_field   = inputs.get('original_taxon_name_field')
        original_author_field       = inputs.get('origin_author_field')
        match_type_field            = inputs.get('match_type_field')
        lsid_field                  = inputs.get('lsid_field')
        fuzzy_match_enabled         = inputs.get('fuzzy_match_enabled')

        if fuzzy_match_enabled is None:
            fuzzy_match_enabled = True

        # look up aphia record for input taxon name in WoRMS taxonomic database
        is_exact_match, aphia_record = (
            self._worms.aphia_record_by_taxon_name(input_record[taxon_name_field], fuzzy_match_enabled))

        if aphia_record is not None:

            # save original taxon name and author values
            _copy_field(input_record, taxon_name_field, original_taxon_name_field)
            _copy_field(input_record, author_field, original_author_field)

            # replace taxon name and author fields in input record with values in aphia record
            _set_field(input_record, taxon_name_field, aphia_record['scientificname'])
            _set_field(input_record, author_field, aphia_record['authority'])

            # add new fields
            _set_field(input_record, match_type_field, 'exact match' if is_exact_match else 'fuzzy match')
            _set_field(input_record, lsid_field, aphia_record['lsid'])

        else:

            _set_field(input_record, original_taxon_name_field, '')
            _set_field(input_record, original_author_field, '')
            _set_field(input_record, match_type_field, 'no match')
            _set_field(input_record, lsid_field, '')

        return {'worms_curated_record': input_record}

def _copy_field(record, from_field, to_field):
     if from_field in record and to_field is not None:
        record[to_field] = record[from_field]

def _set_field(record, field, value):
     if field is not None:
        record[field] = value

if __name__ == '__main__':
    """ Demonstrate standalone usage """
    import sys
    import csv

    options = { 'taxon_name_field'          : 'TaxonName',
                'author_field'              : 'Author',
                'original_taxon_name_field' : 'OriginalTaxonName',
                'original_author_field'     : 'OriginalAuthor',
                'match_type_field'          : 'WoRMSMatchType',
                'lsid_field'                : 'LSID',
                'fuzzy_match_enabled'       : True }

    curator = RecordCurator()
    dr = csv.DictReader(open('data/five_records.csv', 'r'))
    dw = csv.DictWriter(sys.stdout, ['ID', 'TaxonName', 'Author', 'OriginalTaxonName',
                                     'OriginalAuthor', 'WoRMSMatchType', 'LSID'])
    dw.writeheader()
    for record in dr:
        curator.clean_record(record, options)
        dw.writerow(record)
