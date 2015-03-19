
from suds.client import Client

class WoRMSClient(object): 
    
    WORMS_SERVICE_URL = 'http://marinespecies.org/aphia.php?p=soap&wsdl=1'

    def __init__(self):
        self._client = Client(self.WORMS_SERVICE_URL)
        self.marine_only = False

    def lookup_aphia_record_by_exact_taxon_name(self, submitted_name):
        aphia_id = self._client.service.getAphiaID(submitted_name, self.marine_only);
        if aphia_id == None or aphia_id == -999:
            return None
        else:
            aphia_record = self._client.service.getAphiaRecordByID(aphia_id)
            return self.composeMatchResult(submitted_name, aphia_record)

    def lookup_aphia_record_by_fuzzy_taxon_name(self, submitted_name):
        matching_records = self._client.service.matchAphiaRecordsByNames(submitted_name, self.marine_only);
        if len(matching_records) != 1 or len(matching_records[0]) != 1:
            return None
        else:
            return self.composeMatchResult(submitted_name, matching_records[0][0])
  
    def lookup_aphia_record_by_taxon_name(self, submitted_name):    
        exact_match_result = self.lookup_aphia_record_by_exact_taxon_name(submitted_name)
        if exact_match_result != None:
            return exact_match_result
        else:
            return self.lookup_aphia_record_by_fuzzy_taxon_name(submitted_name)
      
    def composeMatchResult(self, submitted_name, aphia_record):
        return {
            'submittedTaxonName'  : submitted_name,
            'returnedTaxonName'   : aphia_record['scientificname'],
            'exactMatch'          : (aphia_record['match_type'] == 'exact'),
            'lsid'                : aphia_record['lsid'],
            'author'              : aphia_record['authority'],
            'aphiaRecord'         : aphia_record
        }


if __name__ == '__main__':
    wc = WoRMSClient()
    print wc.lookup_aphia_record_by_taxon_name('Mollusca')
    print wc.lookup_aphia_record_by_taxon_name('Architectonica reevi')

