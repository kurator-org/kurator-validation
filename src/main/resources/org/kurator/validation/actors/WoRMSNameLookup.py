
from org.kurator.validation.services.WoRMSClient import WoRMSClient

import sys
print sys.path

def start():
    global wc
    wc = WoRMSClient()

def validate(record):
    taxonName = record['TaxonName']
    result = wc.lookUpAphiaRecordByTaxonName(taxonName)
    if result != None:
      record['TaxonName'] = result['returnedTaxonName']
      record['OriginalName'] = result['submittedTaxonName']
      record['OriginalAuthor'] = record['Author']
      record['Author'] = result['author']
      record['lsid'] = result['lsid']
      return record
