
try:
    import java.lang
    import sys
    sys.path =  ['', '/Users/tmcphill/jython2.5.3/Lib', '__classpath__', '__pyclasspath__/', '/Users/tmcphill/jython2.5.3/Lib/site-packages', '/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages', '/Users/tmcphill/GitRepos/kurator-validation/src/main/resources']
except:
  pass
  
from suds.client import Client

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
      return self.composeMatchResult(submittedName, aphiaRecord)

  def lookupAphiaRecordByFuzzyTaxonName(self, submittedName):
    matchingRecords = self.client.service.matchAphiaRecordsByNames(submittedName, self.marineOnly);
    if len(matchingRecords) != 1 or len(matchingRecords[0]) != 1:
      return None
    else:
      return self.composeMatchResult(submittedName, matchingRecords[0][0])
  
  def lookUpAphiaRecordByTaxonName(self, submittedName):    
    result = self.lookupAphiaRecordByExactTaxonName(submittedName)
    if result != None:
      return result
    else:
      return self.lookupAphiaRecordByFuzzyTaxonName(submittedName)
      
  def composeMatchResult(self, submittedName, aphiaRecord):
    return {
      'submittedTaxonName': submittedName,
      'returnedTaxonName': aphiaRecord['scientificname'],
      'exactMatch': (aphiaRecord['match_type'] == 'exact'),
      'lsid': aphiaRecord['lsid'],
      'author':  aphiaRecord['authority'],
      'aphiaRecord': aphiaRecord
    }

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

#if __name__ == '__main__':
#  wc = WoRMSClient()
#  print wc.lookUpAphiaRecordByTaxonName('Mollusca')
#  print wc.lookUpAphiaRecordByTaxonName('Architectonica reevi')

