from suds.client import Client
import re

class WoRMSClient(object): 

  def __init__(self):
    self.WORMS_SERVICE_URL = 'http://marinespecies.org/aphia.php?p=soap&wsdl=1'
    self.client = Client(self.WORMS_SERVICE_URL)
    self.marineOnly = False

  def lookupAphiaRecordByExactTaxonName(self, submittedName):
    aphiaId = self.client.service.getAphiaID(submittedName, self.marineOnly);
    if aphiaId == None or aphiaId == -999:
      return None
    else:
      aphiaRecord = self.client.service.getAphiaRecordByID(aphiaId)
      return AphiaRecordLookupResult(submittedName, aphiaRecord)

  def lookupAphiaRecordByFuzzyTaxonName(self, submittedName):
    matchingRecords = self.client.service.matchAphiaRecordsByNames(submittedName, self.marineOnly);
    if len(matchingRecords) != 1 or len(matchingRecords[0]) != 1:
      return None
    else:
      return AphiaRecordLookupResult(submittedName, matchingRecords[0][0])
  
  def lookUpAphiaRecordByTaxonName(self, submittedName):    
    result = self.lookupAphiaRecordByExactTaxonName(submittedName)
    if result != None:
      return result
    else:
      return self.lookupAphiaRecordByFuzzyTaxonName(submittedName)



class AphiaRecordLookupResult(object):
  
  def __init__(self, submitted, record):
    self.submittedTaxonName = submitted
    self.returnedTaxonName = record['scientificname']
    self.exactMatch = (record['match_type'] == 'exact')
    self.aphiaRecord = record

  def lsid(self):
    return self.aphiaRecord['lsid']

  def author(self):
    return self.aphiaRecord['authority']

  def __repr__(self):
    return (
      'AphiaRecordLookupResult{' + '\n' + 
      '  submittedTaxonName = ' + self.submittedTaxonName + '\n'
      '  returnedTaxonName = ' + self.returnedTaxonName + '\n'
      '  exactMatch = ' + str(self.exactMatch) + '\n'
      '  aphiaId = ' + str(self.aphiaRecord['AphiaID']) + '\n'
      '}'
    )

if __name__ == '__main__':
  wc = WoRMSClient()
  print wc.lookUpAphiaRecordByTaxonName('Mollusca')
  print wc.lookUpAphiaRecordByTaxonName('Architectonica reevi')

