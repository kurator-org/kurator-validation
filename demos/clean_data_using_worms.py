import sys
import csv
import WoRMSClient

##################################################################################################
# @BEGIN clean_data_using_worms
# @PARAM input_data_file_name
# @PARAM cleaned_data_file_name
# @PARAM rejected_data_file_name
# @PARAM input_field_delimiter
# @PARAM output_field_delimiter
# @IN input_data @URI file:{input_data_file_name}
# @OUT cleaned_data  @URI file:{cleaned_data_file_name}
# @OUT rejected_data @URI file:{rejected_data_file_name}

def clean_data_using_worms(
    input_data_file_name, 
    cleaned_records_file_name, 
    rejected_records_file_name, 
    input_field_delimiter=',',
    output_field_delimiter=','
    ):  
    
    worms_client = WoRMSClient.WoRMSClient()

    ##############################################################################################
    # @BEGIN read_input_data_records
    # @PARAM input_data_file_name
    # @PARAM input_field_delimiter
    # @IN input_data @URI file:{input_data_file_name}
    # @OUT original_record
    
    # create CSV reader for input records
    input_data = csv.DictReader(open(input_data_file_name, 'r'),
                                delimiter=input_field_delimiter)

    # iterate over input data records
    for original_record in input_data:
    
    # @END read_input_data_records

    ##############################################################################################
    # @BEGIN extract_record_fields 
    # @IN original_record
    # @OUT original_scientific_name
    # @OUT original_authorship
    
        # extract values of fields to be validated
        original_scientific_name = original_record['scientificName']
        original_authorship = original_record['scientificNameAuthorship']
            
    # @END extract_record_fields 

        
    ##############################################################################################
    # @BEGIN look_up_worms_record 
    # @IN original_scientific_name
    # @OUT matching_worms_record
    # @OUT worms_match_type    
    # @OUT worms_lsid
    
        worms_match_type = None
        worms_lsid = None
        
        # first try exact match of the scientific name against WoRMs
        matching_worms_record = (
            worms_client.aphia_record_by_exact_name(original_record['scientificName']))
        if matching_worms_record is not None:
            worms_match_type = 'exact'
        
        # otherwise try a fuzzy match
        else:
            matching_worms_record = (
                self.aphia_record_by_fuzzy_name(original_record['scientificName']))
            if matching_worms_record is not None:
                worms_match_type = 'fuzzy'
        
        # if either match succeeds extract the LSID for the taxon
        if matching_worms_record is not None:
            worms_lsid = matching_worms_record['lsid']
                    
    # @END look_up_worms_record

    ##############################################################################################
    # @BEGIN reject_records_not_in_worms
    # @IN original_record
    # @IN worms_match_type
    # @PARAM rejected_data_file_name
    # @PARAM output_field_delimiter
    # @OUT rejected_data @URI file:{rejected_records_file_name}
    
        # reject the currect record if not matched successfully against WoRMs
        if worms_match_type is None:

            # open file for storing rejected data if not already open
            if 'rejected_data' not in locals():
                rejected_data = csv.DictWriter(open(rejected_data_file_name, 'w'), 
                                                  oiginal_record.keys() + ["RejectionReason"], 
                                                  delimiter=output_field_delimiter)
                rejected_data.writeheader()
                
            # write current record to rejects file
            rejected_data.writerow(original_record)
            
            # skip to processing of next record in input file
            continue
                
    # @END reject_records_not_in_worms

    ##############################################################################################
    # @BEGIN update_scientific_name
    # @IN original_scientific_name
    # @IN matching_worms_record
    # @IN worms_match_type    
    # @OUT updated_scientific_name
        
        updated_scientific_name = None
        
        # get scientific name from WoRMs record if the taxon name match was fuzzy
        if worms_match_type == 'fuzzy':
            updated_scientific_name = matching_worms_record['scientificname']

    # @END update_scientific_name

    ##############################################################################################
    # @BEGIN update_authorship
    # @IN matching_worms_record
    # @IN original_authorship
    # @OUT updated_authorship
    
        updated_authorship = None
        
        # get the scientific name authorship from the WoRMS record if different from input record
        worms_name_authorship = matching_worms_record['authority']
        if worms_name_authorship != original_authorship:
            updated_authorship = worms_name_authorship

    # @END update_authorship

    ##############################################################################################
    # @BEGIN compose_cleaned_record
    # @IN original_record
    # @IN worms_match_type
    # @IN worms_lsid
    # @IN updated_scientific_name
    # @IN original_scientific_name
    # @IN updated_authorship
    # @IN original_authorship
    # @OUT cleaned_record
       
        cleaned_record = original_record
        cleaned_record['LSID'] = worms_lsid
        
        if updated_scientific_name is not None:
            cleaned_record['scientificName'] = updated_scientific_name
            cleaned_record['originalScientificName'] = original_scientific_name
            
        if updated_authorship is not None:
            cleaned_record['scientificNameAuthorship'] = updated_authorship
            cleaned_record['originalScientificNameAuthorship'] = original_authorship
                
    # @END compose_cleaned_record

    ##############################################################################################
    # @BEGIN write_clean_data_set
    # @PARAM cleaned_data_file_name
    # @PARAM output_field_delimiter
    # @IN cleaned_record
    # @OUT cleaned_data  @URI file:{cleaned_records_file_name}

        # open file for storing cleaned data if not already open
        if 'cleaned_data' not in locals():
            cleaned_record_field_names = cleaned_record.keys() + \
                ['originalScientificName', 'originalAuthor', 'WoRMsMatchType', 'LSID']
            cleaned_data = csv.DictWriter(open(cleaned_records_file_name, 'w'), 
                                          cleaned_record_field_names, 
                                          delimiter=output_field_delimiter)
            cleaned_data.writeheader()
    
        cleaned_data.writerow(cleaned_record)
        
    # @END write_clean_data_set

# @END clean_data_using_worms


if __name__ == '__main__':
    """ Demo of clean_data_using_worms script """

    clean_data_using_worms(
        input_data_file_name='input.csv',
        cleaned_records_file_name='cleaned.csv',
        rejected_records_file_name='rejected.csv',
        input_field_delimiter='\t'
    )
