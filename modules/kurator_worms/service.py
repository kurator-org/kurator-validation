
from suds.client import Client

class WoRMSService(object): 
    """
    Class for accessing the WoRMS taxonomic name database via the AphiaNameService. 
    
    The Aphia names services are described at http://marinespecies.org/aphia.php?p=soap. 
    """
    
    WORMS_APHIA_NAME_SERVICE_URL = 'http://marinespecies.org/aphia.php?p=soap&wsdl=1'

    def __init__(self, marine_only=False):
        """ Initialize a SOAP client using the WSDL for the WoRMS Aphia names service"""        
        self._client = Client(self.WORMS_APHIA_NAME_SERVICE_URL)
        self._marine_only = marine_only

    def aphia_record_by_exact_taxon_name(self, name):
        """
        Perform an exact match on the input name against the taxon names in WoRMS.
        
        This function first invokes an Aphia names service to lookup the Aphia ID for
        the taxon name.  If exactly one match is returned, this function retrieves the
        Aphia record for that ID and returns it. 
        """        
        aphia_id = self._client.service.getAphiaID(name, self._marine_only);
        if aphia_id is None or aphia_id == -999:         # -999 indicates multiple matches
            return None
        else:
            return self._client.service.getAphiaRecordByID(aphia_id)

    def aphia_record_by_fuzzy_taxon_name(self, name):
        """
        Perform fuzzy match search for the input name against the taxon names in WoRMS.
        
        The invoked Aphia names service returns a list of list matches.  This function 
        returns a match only if exactly one match is returned by the AphiaNameService. 
        """        
        matches = self._client.service.matchAphiaRecordsByNames(name, self._marine_only);
        if len(matches) == 1 and len(matches[0]) == 1:
            return matches[0][0]
        else:
            return None
  
    def aphia_record_by_taxon_name(self, name, fuzzy_match_enabled=True):
        """
        Perform exact and fuzzy match searches as needed to lookup the input taxon name 
        in WoRMS.
        
        Returns a tuple with two elements.  The first is a boolean value indicating if an
        exact match to the input taxon name was found.  The second element of the
        returned tuple is the result of calling aphia_record_by_exact_taxon_name() if an 
        exact match is found, or the results of calling aphia_record_by_fuzzy_taxon_name() 
        otherwise.  A fuzzy match (a slow operation) is performed only if the exact match 
        (a fast operation) fails.
        """
        exact_match_result = self.aphia_record_by_exact_taxon_name(name)
        if exact_match_result is not None:
            return True, exact_match_result
        else:
            if fuzzy_match_enabled:
                fuzzy_match_result = self.aphia_record_by_fuzzy_taxon_name(name)
                return False, fuzzy_match_result          
            else:
                return False, None
                      
if __name__ == '__main__':
    """ Demonstration of class usage"""

    # create an instance of WoRMSService
    ws = WoRMSService()
    
    # Use the exact taxon name lookup service
    matched_record = ws.aphia_record_by_exact_taxon_name('Mollusca')
    print matched_record['scientificname']

    # Use the fuzzy taxon name lookup service
    matched_record = ws.aphia_record_by_fuzzy_taxon_name('Architectonica reevi')
    print matched_record['scientificname']
    
    # use the automatic failover from exact to fuzzy name lookup
    was_exact_match, matched_record = ws.aphia_record_by_taxon_name('Architectonica reevi')
    print matched_record['scientificname']
    print was_exact_match

