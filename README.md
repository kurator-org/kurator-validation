Kurator-Validation
==================

The [kurator-validation](https://github.com/kurator-org/kurator-validation) repository provides libraries, actors, and workflows for validating and cleaning biodiversity data. The code libraries may be used directly from Python scripts, while the actors and workflows are designed to run within the **[Kurator-Akka](https://github.com/kurator-org/kurator-akka)** framework.  This software is being developed as part of the [Kurator project](http://wiki.datakurator.net/web/Kurator).

This README describes how one Python class in the library, [WoRMSService](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/python/kurator/validation/services/WoRMSService.py), can be used either directly within a Python script or as an actor in an Akka-based [workflow](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/org/kurator/validation/workflows/WoRMS_name_validation.yaml).  Both the script and the workflow validate and correct the scientific name and authorship fields in a set of input specimen records using the [WoRMS web service](http://marinespecies.org/aphia.php?p=webservice) to look up taxon names in the standard WoRMS taxononmy.

Other Python classes made available through this package may be used similarly.  We recommend using the approaches described in this README to develop, test, and distribute your own data curation classes, packages, actors, and workflows that work with the Kurator software toolkit.

For information about the **Kurator-Akka** workflow framework please see the [README](https://github.com/kurator-org/kurator-akka/blob/master/README.md) in the [Kurator-Akka](https://github.com/kurator-org/kurator-akka) repository

Structure of this repository
----------------------------

##### Maven project layout

The overall structure of the kurator-validation repository is as a Maven project.  This structure makes it easy to test the libraries, scripts, actors, and workflows using Java-based tools and to employ the Bamboo continuous build server at NCSA.  This structure also facilitates the use of Python libraries and actors from the (Java-based) **Kurator-Akka** framework.

Overall structure of the repository:

Directory            | Description
---------------------|------------
src/main/python      | Python sources for libraries, scripts, and actors.
src/test/java        | Source code for Java-based tests of actors and workflows.
src/test/resources   | Resource files available to Java-based tests.

##### Python library layout

All python code provided with kurator-validation is organized in a single directory tree at `src/main/python`.  This directory tree is structured so that all code is in sub-packages of the `org.kurator.validation` Python package.

Subdirectories of the `src/main/python` directory include:

Directory                            | Description
-------------------------------------|------------
org/kurator/validation/**actors**    | Sources for python-based actors.
org/kurator/validation/**scripts**   | Python scripts using the data cleaning services and actors.
org/kurator/validation/**services**  | Python classes and functions providing data cleaning services.
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

#### The WoRMSCurator actor

#### A YAML declaration of a workflow that uses the WoRMSCurator actor