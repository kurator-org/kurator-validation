import sys
import csv
import WoRMSClient
import time
from datetime import datetime

##################################################################################################
# @BEGIN clean_data_using_worms
# @PARAM input_data_file_name
# @PARAM cleaned_data_file_name
# @PARAM rejected_data_file_name
# @PARAM input_field_delimiter
# @PARAM output_field_delimiter
# @IN input_data @FILE file:{input_data_file_name}
# @OUT cleaned_data  @FILE file:{cleaned_data_file_name}
# @OUT rejected_data @FILE file:{rejected_data_file_name}

def clean_data_using_worms(
    input_data_file_name, 
    cleaned_data_file_name, 
    rejected_data_file_name, 
    input_field_delimiter=',',
    output_field_delimiter=','
    ):  
    
    worms_client = WoRMSClient.WoRMSClient()
    accepted_record_count = 0
    rejected_record_count = 0

    ##############################################################################################
    # @BEGIN read_input_data_records
    # @PARAM input_data_file_name
    # @PARAM input_field_delimiter
    # @IN input_data @FILE file:{input_data_file_name}
    # @OUT original_record
    
    # create CSV reader for input records
    timestamp("Reading input records from '{0}'.".format(input_data_file_name))
    input_data = csv.DictReader(open(input_data_file_name, 'r'),
                                delimiter=input_field_delimiter)

    # iterate over input data records
    record_num = 0
    for original_record in input_data:
        
        record_num += 1
        print
        timestamp('Reading input record {0:03d}.'.format(record_num))
    
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
    # @BEGIN find_matching_worms_record 
    # @IN original_scientific_name
    # @OUT matching_worms_record
    # @OUT worms_lsid
    
        worms_match_result = None
        worms_lsid = None
        
        # first try exact match of the scientific name against WoRMs
        timestamp("Trying WoRMs EXACT match for scientific name: '{0}'.".format(original_scientific_name))
        matching_worms_record = worms_client.aphia_record_by_exact_name(original_scientific_name)
        if matching_worms_record is not None:
            timestamp('WoRMs EXACT match was SUCCESSFUL.')
            worms_match_result = 'exact'

        # otherwise try a fuzzy match
        else:
            timestamp('EXACT match FAILED.')      
            timestamp("Trying WoRMs FUZZY match for scientific name: '{0}'.".format(original_scientific_name))
            matching_worms_record = worms_client.aphia_record_by_fuzzy_name(original_scientific_name)
            if matching_worms_record is not None:
                timestamp('WoRMs FUZZY match was SUCCESSFUL.')
                worms_match_result = 'fuzzy'
            else:
                timestamp('WoRMs FUZZY match FAILED.')
        
        # if either match succeeds extract the LSID for the taxon
        if matching_worms_record is not None:
            worms_lsid = matching_worms_record['lsid']
                    
    # @END find_matching_worms_record

    ##############################################################################################
    # @BEGIN reject_records_not_in_worms
    # @IN original_record
    # @IN matching_worms_record
    # @PARAM rejected_data_file_name
    # @PARAM output_field_delimiter
    # @OUT rejected_data @FILE file:{rejected_data_file_name}
    
        # reject the currect record if not matched successfully against WoRMs
        if worms_match_result is None:

            # open file for storing rejected data if not already open
            if 'rejected_data' not in locals():
                rejected_data = csv.DictWriter(open(rejected_data_file_name, 'w'), 
                                                  input_data.fieldnames, 
                                                  delimiter=output_field_delimiter)
                rejected_data.writeheader()
                
            # write current record to rejects file
            timestamp('REJECTED record {0:03d}.'.format(record_num))
            rejected_data.writerow(original_record)
            rejected_record_count += 1
            
            # skip to processing of next record in input file
            continue
                
    # @END reject_records_not_in_worms

    ##############################################################################################
    # @BEGIN update_scientific_name
    # @IN original_scientific_name
    # @IN matching_worms_record
    # @OUT updated_scientific_name
        
        updated_scientific_name = None
        
        # get scientific name from WoRMs record if the taxon name match was fuzzy
        if worms_match_result == 'fuzzy':
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
    # @IN worms_lsid
    # @IN updated_scientific_name
    # @IN original_scientific_name
    # @IN updated_authorship
    # @IN original_authorship
    # @OUT cleaned_record
       
        cleaned_record = original_record
        cleaned_record['LSID'] = worms_lsid
        cleaned_record['WoRMsMatchResult'] = worms_match_result
        
        if updated_scientific_name is not None:
            timestamp("UPDATING scientific name from '{0}' to '{1}'.".format(
                     original_scientific_name, updated_scientific_name))
            cleaned_record['scientificName'] = updated_scientific_name
            cleaned_record['originalScientificName'] = original_scientific_name
            
        if updated_authorship is not None:
            timestamp("UPDATING scientific name authorship from '{0}' to '{1}'.".format(
                original_authorship, updated_authorship))
            cleaned_record['scientificNameAuthorship'] = updated_authorship
            cleaned_record['originalAuthor'] = original_authorship
                
    # @END compose_cleaned_record

    ##############################################################################################
    # @BEGIN write_clean_data_set
    # @PARAM cleaned_data_file_name
    # @PARAM output_field_delimiter
    # @IN cleaned_record
    # @OUT cleaned_data  @FILE file:{cleaned_data_file_name}

        # open file for storing cleaned data if not already open
        if 'cleaned_data' not in locals():
            cleaned_record_field_names = input_data.fieldnames + \
                ['LSID', 'WoRMsMatchResult', 'originalScientificName', 'originalAuthor']
            cleaned_data = csv.DictWriter(open(cleaned_data_file_name, 'w'), 
                                          cleaned_record_field_names, 
                                          delimiter=output_field_delimiter)
            cleaned_data.writeheader()
    
        timestamp('ACCEPTED record {0:03d}.'.format(record_num))
        cleaned_data.writerow(cleaned_record)
        accepted_record_count += 1
        
    # @END write_clean_data_set

    print
    timestamp("Wrote {0} accepted records to '{1}'.".format(accepted_record_count, cleaned_data_file_name))
    timestamp("Wrote {0} rejected records to '{1}'.".format(rejected_record_count, rejected_data_file_name))

# @END clean_data_using_worms


def timestamp(message):
    current_time = time.time()
    timestamp = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
    print "{0}  {1}".format(timestamp, message)


if __name__ == '__main__':
    """ Demo of clean_data_using_worms script """

    clean_data_using_worms(
        input_data_file_name='input.csv',
        cleaned_data_file_name='cleaned.csv',
        rejected_data_file_name='rejected.csv'
    )
