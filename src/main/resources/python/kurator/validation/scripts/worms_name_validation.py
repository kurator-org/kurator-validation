
import sys
import csv

sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources/python')
from kurator.validation.actors.WoRMSNameLookup import start as startActor
from kurator.validation.actors.WoRMSNameLookup import validate as validateRecord

inputfile = "/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv"

data = []
with open(inputfile, "r") as infile, open('out.csv', 'w') as outfile:
  dr = csv.DictReader(infile)
  dw = csv.DictWriter(outfile, ['ID','TaxonName','Author','OriginalName','OriginalAuthor','lsid'])
  dw.writeheader()
  startActor()
  for record in dr:
      validateRecord(record)
      dw.writerow(record)
    
