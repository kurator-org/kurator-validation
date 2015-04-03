
from kurator.validation.services.WoRMSClient import WoRMSClient

def start():
    global worms_client
    worms_client = WoRMSClient()

def curate(input_record):

    # look up aphia record for input taxon name in WoRMS taxonomic database
    is_exact_match, aphia_record = (
        worms_client.aphia_record_by_taxon_name(input_record['TaxonName']))
    if aphia_record is not None:
    
        # save taxon name and author values from input record in new fields
        input_record['OriginalName'] = input_record['TaxonName']
        input_record['OriginalAuthor'] = input_record['Author']

        # replace taxon name and author fields in input record with values in aphia record
        input_record['TaxonName'] = aphia_record['scientificname']
        input_record['Author'] = aphia_record['authority']
      
        # add new fields
        input_record['WoRMsExactMatch'] = is_exact_match
        input_record['lsid'] = aphia_record['lsid']
        
    else:
      
        input_record['OriginalName'] = None
        input_record['OriginalAuthor'] = None
        input_record['WoRMsExactMatch'] = None
        input_record['lsid'] = None

    return input_record
