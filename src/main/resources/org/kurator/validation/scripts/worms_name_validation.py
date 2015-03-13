import sys
sys.path.append('/Users/tmcphill/GitRepos/kurator-validation/src/main/resources')
from org.kurator.validation.services.WoRMSClient import WoRMSClient
from org.kurator.validation.services.WoRMSClient import start
from org.kurator.validation.services.WoRMSClient import validate
import csv

from suds.client import Client

inputfile = "/Users/tmcphill/GitRepos/kurator-validation/src/test/resources/org/kurator/validation/data/testinput_moll.csv"

data = []
with open(inputfile, "r") as infile, open('out.csv', 'w') as outfile:
  wc = WoRMSClient()
  dr = csv.DictReader(infile)
  fieldnames = ['ID','TaxonName','Author','OriginalName','OriginalAuthor','lsid']
  dw = csv.DictWriter(outfile, fieldnames)
  dw.writeheader()
  start()
  for record in dr:
      validate(record)
      dw.writerow(record)
    
