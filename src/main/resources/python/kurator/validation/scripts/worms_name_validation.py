
import sys
import csv

sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources/python')
from kurator.validation.actors.WoRMSNameLookup import start as start_actor
from kurator.validation.actors.WoRMSNameLookup import validate as validate_record

inputfile = "/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv"

data = []
with open(inputfile, "r") as infile, open('out.csv', 'w') as outfile:
  dr = csv.DictReader(infile)
  dw = csv.DictWriter(outfile, ['ID','TaxonName','Author','OriginalName','OriginalAuthor','lsid'])
  dw.writeheader()
  start_actor()
  for record in dr:
      validate_record(record)
      dw.writerow(record)
    
