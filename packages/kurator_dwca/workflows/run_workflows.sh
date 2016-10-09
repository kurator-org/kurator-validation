ka -f dwca_controlled_term_assessor.yaml -p workspace=./ws_term_assessor -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_geography_assessor.yaml -p workspace=./ws_geography_assessor -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_geography_cleaner.yaml -p workspace=./ws_geography_cleaner -p dwca_url=http://web.macs.ualberta.ca:8088/ipt/archive?r=uamz-herpetology
ka -f dwca_term_values.yaml -p workspace=./ws_term_values -p dwca_url=http://ipt.vertnet.org:8080/ipt/archive.do?r=dmnh_eggs -p fieldlist="family|genus|specificepithet|infraspecificepithet"
ka -f darwinize_file.yaml -p workspace=./darwinize_file_workspace -p format=txt -p inputfile=../data/tests/test_barcelona1.txt -p dwcnamespace=y
ka -f vocabulary_maker.yaml -p workspace=./vocab_maker_workspace -p inputfile=./darwinize_file_workspace/darwinized_file.txt -p vocabfile=collectors.csv -p termlist=recordedBy -p key=collectorname
ka -f dwca_geography_assessor.yaml -p workspace=./ws_geography_assessor -p dwca_url=http://pontos.fwl.oregonstate.edu:8080/ipt/archive.do?r=oregonstate_fish
ka -f dwca_geography_cleaner.yaml -p workspace=./ws_geography_cleaner -p dwca_url=http://pontos.fwl.oregonstate.edu:8080/ipt/archive.do?r=oregonstate_fish
ka -f file_aggregator.yaml -p workspace=./file_aggregator_workspace -p inputfile1=../data/tests/test_barcelona1.txt -p inputfile2=../data/tests/test_barcelona2.txt -p outputfile=aggregated_file.csv -p format=csv
