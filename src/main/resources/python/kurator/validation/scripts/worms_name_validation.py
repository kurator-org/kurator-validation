
import sys
import csv

sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources/python')
from kurator.validation.actors.WoRMSActor import WoRMSActor

inputfile = '/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv'

with open(inputfile, 'r') as infile, open('out.csv', 'w') as outfile:
    dr = csv.DictReader(infile)
    dw = csv.DictWriter(outfile, ['ID', 'TaxonName', 'Author', 'OriginalName', 
                                  'OriginalAuthor', 'WoRMsExactMatch', 'lsid'])
    dw.writeheader()
    actor = WoRMSActor()
    for record in dr:
        actor.curate_taxon_name_and_author(record)
        dw.writerow(record)
