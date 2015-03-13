import sys
sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources')
from org.kurator.validation.services.WoRMSClient import WoRMSClient
from org.kurator.validation.services.WoRMSClient import start as startActor
from org.kurator.validation.services.WoRMSClient import validate as validateRecord
import csv

from suds.client import Client

inputfile = "/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv"

data = []
with open(inputfile, "r") as infile, open('out.csv', 'w') as outfile:
  wc = WoRMSClient()
  dr = csv.DictReader(infile)
  dw = csv.DictWriter(outfile, ['ID','TaxonName','Author','OriginalName','OriginalAuthor','lsid'])
  dw.writeheader()
  startActor()
  for record in dr:
      validateRecord(record)
      dw.writerow(record)
    
