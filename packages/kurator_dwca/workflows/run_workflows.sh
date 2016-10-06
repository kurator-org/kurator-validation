ka -f dwca_controlled_term_assessor.yaml -p workspace=./ws_term_assessor -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_geography_assessor.yaml -p workspace=./ws_geography_assessor -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_geography_cleaner.yaml -p workspace=./ws_geography_cleaner -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_term_values.yaml -p workspace=./ws_term_values -p dwca_url=http://ipt.vertnet.org:8080/ipt/archive.do?r=dmnh_eggs -p fieldlist="family|genus|specificepithet|infraspecificepithet"
