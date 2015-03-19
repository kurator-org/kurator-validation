
from kurator.validation.services.WoRMSClient import WoRMSClient

def start():
    global worms_client
    worms_client = WoRMSClient()

def validate(record):
    taxonName = record['TaxonName']
    result = worms_client.lookup_aphia_record_by_taxon_name(taxonName)
    if result != None:
      record['TaxonName'] = result['returnedTaxonName']
      record['OriginalName'] = result['submittedTaxonName']
      record['OriginalAuthor'] = record['Author']
      record['Author'] = result['author']
      record['lsid'] = result['lsid']
      return record
