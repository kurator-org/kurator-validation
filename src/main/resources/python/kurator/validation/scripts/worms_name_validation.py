
import sys
import csv

sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources/python')
from kurator.validation.actors import WoRMSActor

inputfile = '/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv'

with open(inputfile, 'r') as infile, open('out.csv', 'w') as outfile:
    dr = csv.DictReader(infile)
    dw = csv.DictWriter(outfile, ["ID", 'TaxonName', 'Author', 'OriginalName', 'OriginalAuthor', 'lsid'])
    dw.writeheader()
    WoRMSActor.start()
    for record in dr:
        WoRMSActor.curate(record)
        dw.writerow(record)
