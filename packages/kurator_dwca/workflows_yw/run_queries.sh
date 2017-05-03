#!/usr/bin/env bash -l
#
# ./run_queries.sh &> run_queries.txt

xsb --quietload --noprompt --nofeedback --nobanner << END_XSB_STDIN

[rules].
[extractfacts].
[modelfacts].
[reconfacts].
[queries].

printall('eq1(SourceFile) - What source files SF were YW annotations extracted from?', eq1(_)).
printall('eq2(ProgramName) - What are the names N of all program blocks?', eq2(_)).
printall('eq3(PortName) - What out ports are qualified with URIs?', eq3(_)).

printall('mq1(SourceFile,StartLine,EndLine) - Where is the definition of block FileTermCounterWorkflow.count_field_values?', mq1(_,_,_)).
printall('mq2(WorkflowName,Description) - What is the name and description of the top-level workflow?', mq2(_,_)).
printall('mq3(FunctionName) - What are the names of any top-level functions?', mq3(_)).
printall('mq4(ProgramName) -  What are the names of the programs comprising the top-level workflow?', mq4(_)).
printall('mq5(DataName) - What are the names and descriptions of the inputs to the top-level workflow?', mq5(_,_)).
printall('mq6(DataName) - What data is output by program block count_field_values?', mq6(_)).
printall('mq7(ProgramName) - What program blocks provide input directly to count_field_values?', mq7(_)).
printall('mq8(ProgramName) - What programs have input ports that receive data FileTermCounterWorkflow.fieldlist?', mq8(_)).
printall('mq9(PortCount) - How many ports read data FileTermCounterWorkflow.workflow_workspace?', mq9(_)).
printall('mq10(DataCount) - How many data are read by more than port in workflow FileTermCounterWorkflow?', mq10(_)).
printall('mq11(ProgramName) - What program blocks are immediately downstream of get_interest_list_in_inputfile?', mq11(_)).
printall('mq12(UpstreamProgramName) - What program blocks are immediately upstream of count_term_value?', mq12(_)).
printall('mq13(UpstreamProgramName) - What program blocks are upstream of count_term_value?', mq13(_)).
printall('mq14(DownstreamProgramName) - What program blocks are anywhere downstream of clean_header?', mq14(_)).
printall('mq15(DownstreamDataName) - What data is immediately downstream of encoding?', mq15(_)).
printall('mq16(UpstreamDataName) - What data is immediately upstream of encoding?', mq16(_)).
printall('mq19(UriVariableName) - What URI variables are associated with writes of data FileTermCounterWorkflow.term_value_count_report?', mq19(_)).

printall('rq0(VarName, VarValue) - What URI variable values are associated with resource file_term_values_workspace/count_genus.txt?', rq0(_,_)).
printall('rq1(format) - What format was the run of the script input?', rq1(_)).
printall('rq2(field) - What fieldlist were used during cleaning the header of input file?', rq2(_)).
printall('rq5(sub_fields) - What sub-fields held the field genus from which file_term_values_workspace/count_genus.txt was derived?', rq5(_)).

END_XSB_STDIN