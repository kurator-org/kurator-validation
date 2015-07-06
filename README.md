Kurator-Validation
==================

The [kurator-validation](https://github.com/kurator-org/kurator-validation) repository provides libraries, actors, and workflows for validating and cleaning biodiversity data. The code libraries may be used directly from Python scripts, while the actors and workflows are designed to run within the **[Kurator-Akka](https://github.com/kurator-org/kurator-akka)** framework.  This software is being developed as part of the [Kurator project](http://wiki.datakurator.net/web/Kurator).

This README describes how one Python class in the library, [WoRMSService](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/python/kurator/validation/services/WoRMSService.py), can be used either directly within a Python script or as an actor in an Akka-based [workflow](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/org/kurator/validation/workflows/WoRMS_name_validation.yaml).  Both the script and the workflow validate and correct the scientific name and authorship fields in a set of input specimen records using the [WoRMS web service](http://marinespecies.org/aphia.php?p=webservice) to look up taxon names in the standard WoRMS taxononmy.

Other Python classes made available through this package may be used similarly.  We recommend using the approaches described in this README to develop, test, and distribute your own data curation classes, packages, actors, and workflows that work with the Kurator software toolkit.

For information about the **Kurator-Akka** workflow framework please see the [README](https://github.com/kurator-org/kurator-akka/blob/master/README.md) in the [Kurator-Akka](https://github.com/kurator-org/kurator-akka) repository.

Structure of this repository
----------------------------

##### Maven project layout

The overall structure of the kurator-validation repository is as a Maven project.  This structure makes it easy to test the libraries, scripts, actors, and workflows using Java-based tools and to employ the Bamboo continuous build server at NCSA.  This structure also facilitates the use of Python libraries and actors from the (Java-based) **Kurator-Akka** framework.

Overall structure of the repository:

Directory            | Description
---------------------|------------
src/main/python      | Python sources for function and class libraries, scripts, and actors.
src/test/java        | Source code for Java-based tests of actors and workflows.
src/test/resources   | Resource files available to Java-based tests.

##### Python library layout

All python code provided with kurator-validation is organized in a single directory tree at `src/main/python`.  This directory tree is structured so that all code is in sub-packages of the `org.kurator.validation` Python package.

Subdirectories of the `src/main/python` directory include:

Directory                            | Description
-------------------------------------|------------
org/kurator/validation/**actors**    | Sources for Python-based actors.
org/kurator/validation/**scripts**   | Python scripts using the data cleaning services and actors.
org/kurator/validation/**services**  | Python classes and functions providing data cleaning services including access to remote data sources and network-based services.
org/kurator/validation/standards     | Support for various data standards.
org/kurator/validation/utilities     | General purpose Python scripts and classes.
org/kurator/validation/**workflows** | Workflows composed from actors and declared in YAML.

The **actors**, **scripts**, **services**, and **workflows** directories each provide different ways of accessing the data cleaning capabilities provided by this software. The next section of this README illustrates how to use each approach.

Example: Validating names using WoRMS
-------------------------------------
This section demonstrates how one can validate, correct, or reject data using a specific web service as a reference. The [WoRMS web service](http://marinespecies.org/aphia.php?p=webservice) allows the standard WoRMS taxononmy to be searched by taxon name.  The search may be for an exact match, or for similar names using a fuzzy match.  The kurator-validation package provides (1) a Python class for invoking the WoRMS web service; (2) an example script using this class to access the service and thereby clean a data set; (3) a Python-based actor for performing this service within the context of a **Kurator-Akka** workflow; and (4) a declaration of a workflow using this actor.

#### The WoRMSService class

The Python class defined in [WoRMSService.py](https://github.com/kurator-org/kurator-validation/blob/master/src/main/python/org/kurator/validation/services/WoRMSService.py) makes it easy to use the taxonomic record lookup services provided by the [World Register of Marine Species (WoRMS)](http://marinespecies.org/).  The `WoRMSService` class makes SOAP web service calls on behalf of Python scripts using the class. It provides the following three methods:

    aphia_record_by_exact_taxon_name(name)
    aphia_record_by_fuzzy_taxon_name(name)
    aphia_record_by_taxon_name(name)

The third method calls the other two as needed, first attempting an exact match, then trying a fuzzy match if the exact match fails.

The `__main__` block at the end of [WoRMSService.py](https://github.com/kurator-org/kurator-validation/blob/master/src/main/python/org/kurator/validation/services/WoRMSService.py) illustrates how to use the service:

    # create an instance of WoRMSService
    ws = WoRMSService()

    # Use the exact taxon name lookup service
    matched_record = ws.aphia_record_by_exact_taxon_name('Mollusca')
    print matched_record['scientificname']

    # Use the fuzzy taxon name lookup service
    matched_record = ws.aphia_record_by_fuzzy_taxon_name('Architectonica reevi')
    print matched_record['scientificname']

    # use the automatic failover from exact to fuzzy name lookup
    was_exact_match, matched_record = ws.aphia_record_by_taxon_name('Architectonica reevi')
    print matched_record['scientificname']
    print was_exact_match

You can run this code simply by running `WoRMSService.py` as a standalone Python script.  However, you first will need to install the [suds-jurko](https://pypi.python.org/pypi/suds-jurko/0.6) (lightweight SOAP client package) using `pip`:

	$ pip install suds-jurko

Now you can run the  `WoRMSService.py` demonstration:

    $ python WoRMSService.py
    Mollusca
    Architectonica reevei
    Architectonica reevei
    False
    $

#### A data cleaning script that uses the WoRMSService class directly

The `WoRMSService` class can be used in other scripts that import the class definition.  The class can be imported using the following statement :

    from org.kurator.validation.services.WoRMSService import WoRMSService

In order for Python to find the `org.kurator.validation.services.WoRMSService` package, the directory containing the root of this package must be present in the `PYTHONPATH` environment variable (`JYTHONPATH` if using Jython).

The script [clean_data_using_worms.py](https://github.com/kurator-org/kurator-validation/blob/master/src/main/python/org/kurator/validation/scripts/WoRMS/clean_data_using_worms.py) illustrates how `WoRMSService` can be used in a standalone Python script.  The script also illustrates the use of [YesWorkflow](https://github.com/yesworkflow-org/yw-prototypes) comments to document how data flows through the various operations in the script.  The YesWorkflow rendering of the *process view* of this script is as follows:

![process view of clean_data_using_worms.py](https://raw.githubusercontent.com/kurator-org/kurator-validation/master/src/main/python/org/kurator/validation/scripts/WoRMS/process.png)

The process view reveals only the data processing steps (green blocks in the figure above) identified by YesWorkflow annotations in the script comments. As illustrated in the figure, the script takes as input a set of records (in CSV format), attempts to find corresponding records in the WoRMS taxonomy, rejects input records that cannot be found in WoRMS, and corrects the scientific name and authorship fields as needed in the records that it does find matches for.  The rejected and accepted (poossibly corrected) records are output separately.

The arrows between the blocks above represent their dataflow dependencies, but the data items themselves are hidden.  The *combined view*, below, represents the process blocks together with the data (yellow rounded blocks) and parameters (white rounded blocks) that each processing step consumes and produces:

![combined view of clean_data_using_worms.py](https://raw.githubusercontent.com/kurator-org/kurator-validation/master/src/main/python/org/kurator/validation/scripts/WoRMS/combined.png)


Besides revealing the input, intermediate, and output data items produced by a run of the script (the yellow rounded boxes), this figure shows that the names of the input and output files are named by the parameters `input_data_file_name`, `rejected_data_file_name`, and `cleaned_data_file_name`.

The `__main__` block at the end of [clean_data_using_worms.py](https://github.com/kurator-org/kurator-validation/blob/master/src/main/python/org/kurator/validation/scripts/WoRMS/clean_data_using_worms.py) demonstrates the use of the script using the input file `demo_input.csv` which is provided in the directory with the script:

    if __name__ == '__main__':
        """ Demo of clean_data_using_worms script """

        clean_data_using_worms(
            input_data_file_name='demo_input.csv',
            cleaned_data_file_name='demo_cleaned.csv',
            rejected_data_file_name='demo_rejected.csv'
        )

The records successfully cleaned are stored in the file 'demo_cleaned.csv', while those that could not be repaired are stored in `demo_rejected.csv'.

The first few lines of output when running this demonstration are:

    $ python clean_data_using_worms.py 
    2015-07-05 23:50:57  Reading input records from 'demo_input.csv'.

    2015-07-05 23:50:57  Reading input record 001.
    2015-07-05 23:50:57  Trying WoRMs EXACT match for scientific name: 'Placopecten magellanicus'.
    2015-07-05 23:50:57  WoRMs EXACT match was SUCCESSFUL.
    2015-07-05 23:50:57  UPDATING scientific name authorship from 'Gmelin, 1791' to '(Gmelin, 1791)'.
    2015-07-05 23:50:57  ACCEPTED record 001.

    2015-07-05 23:50:57  Reading input record 002.
    2015-07-05 23:50:57  Trying WoRMs EXACT match for scientific name: 'Placopecten magellanicus'.
    2015-07-05 23:50:58  WoRMs EXACT match was SUCCESSFUL.
    2015-07-05 23:50:58  ACCEPTED record 002.

    2015-07-05 23:50:58  Reading input record 003.
    2015-07-05 23:50:58  Trying WoRMs EXACT match for scientific name: 'magellanicus placopecten'.
    2015-07-05 23:50:59  EXACT match FAILED.
    2015-07-05 23:50:59  Trying WoRMs FUZZY match for scientific name: 'magellanicus placopecten'.
    2015-07-05 23:51:04  WoRMs FUZZY match FAILED.
    2015-07-05 23:51:04  REJECTED record 003.

    2015-07-05 23:51:04  Reading input record 004.
    2015-07-05 23:51:04  Trying WoRMs EXACT match for scientific name: 'Placopecten magellanicus'.
    2015-07-05 23:51:05  WoRMs EXACT match was SUCCESSFUL.
    2015-07-05 23:51:05  UPDATING scientific name authorship from '' to '(Gmelin, 1791)'.
    2015-07-05 23:51:05  ACCEPTED record 004.

#### The WoRMSCurator actor

#### A YAML declaration of a workflow that uses the WoRMSCurator actor