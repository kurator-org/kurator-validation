
from kurator_worms.service import WoRMSService

import sys

_worms = None

def discard_records_not_matching_worms(inputs):

    # create a static instance of WoRMService if needed
    global _worms
    if (_worms is None):
        _worms = WoRMSService()

    # extract input record and configured field names from input
    input_record     = inputs.get('input_record')
    taxon_name_field = inputs.get('taxon_name_field')
    author_field     = inputs.get('author_field')

    # discard input record if no taxon name was provided
    if taxon_name_field is None or input_record.get(taxon_name_field) is None:
        sys.stderr.write('No taxon name provided\n')
        return (None)

    # discard input record if no author name was provided
    if author_field is None or input_record.get(author_field) is None:
        sys.stderr.write('No author name provided\n')
        return None

    # look up aphia record in WoRMS for exact taxon name in input record
    input_taxon_name = input_record[taxon_name_field]
    aphia_record = _worms.aphia_record_by_exact_taxon_name(input_taxon_name)

    # discard the input record if no exact name match was found
    if aphia_record is None:
        sys.stderr.write("No exact name match found for '" + input_taxon_name + "'\n")
        return None

    # discard input record author name does not match that returned by WoRMS
    input_author_name = input_record[author_field]
    if input_author_name != aphia_record['authority']:
        sys.stderr.write("Author names for '" + input_taxon_name + "' do not match\n")
        return None

    # return input record if all above tests passed
    return {'worms_matched_record': input_record}

if __name__ == '__main__':
    """ Demonstrate standalone usage. Example:
           jython record_filter.py  1> accepted.csv 2> filter.log
    """
    import sys
    import csv

    options = { 'taxon_name_field'          : 'TaxonName',
                'author_field'              : 'Author' }

    dr = csv.DictReader(open('data/seven_records.csv', 'r'))
    dw = csv.DictWriter(sys.stdout, ['ID', 'TaxonName', 'Author', 'OriginalTaxonName',
                                     'OriginalAuthor', 'WoRMSMatchType', 'LSID'])
    dw.writeheader()
    for record in dr:
        accepted_record = discard_records_not_matching_worms(record, options)
        if accepted_record is not None:
            dw.writerow(record)
