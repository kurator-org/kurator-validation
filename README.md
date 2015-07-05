Kurator-Validation
==================

The [kurator-validation](https://github.com/kurator-org/kurator-validation) repository provides libraries, actors, and workflows for validating and cleaning biodiversity data. The code libraries may be used directly from Python scripts, while the actors and workflows are designed to run within the **[Kurator-Akka](https://github.com/kurator-org/kurator-akka)** framework.  This software is being developed as part of the [Kurator project](http://wiki.datakurator.net/web/Kurator).

This README describes how one Python class in the library, [WoRMSService](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/python/kurator/validation/services/WoRMSService.py), can be used either directly within a Python script or as an actor in an Akka-based [workflow](https://github.com/kurator-org/kurator-validation/blob/master/src/main/resources/org/kurator/validation/workflows/WoRMS_name_validation.yaml).  Both the script and the workflow validate and correct the scientific name and authorship fields in a set of input specimen records using the [WoRMS web service](http://marinespecies.org/aphia.php?p=webservice) to look up taxon names in the standard WoRMS taxononmy.

Other Python classes made available through this package may be used similarly.  We recommend using the approaches described in this README to develop, test, and distribute your own data curation classes, packages, actors, and workflows that work with the Kurator software toolkit.

For information about the **Kurator-Akka** workflow framework please see the [README](https://github.com/kurator-org/kurator-akka/blob/master/README.md) in the [Kurator-Akka](https://github.com/kurator-org/kurator-akka) repository

Structure of this repository
----------------------------

##### Maven project layout

The overall structure of the kurator-validation repository is as a Maven project.  This structure makes it easy to test the libraries, scripts, actors, and workflows using Java-based tools and to employ the Bamboo continuous build server at NCSA.  This structure also facilitates the use of Python libraries and actors from the **Kurator-Akka** framework (which is Java based).  Finally, the kurator-validation package provides additional data cleaning actors implemented entirely in Java.

Directory            | Description
---------------------|------------
src/main/python      | Python sources for libraries, scripts, and actors.
src/main/java        | Source code for Java-based actors.
src/main/resources   | Resource files used by Kurator-Akka framework.
src/test/java        | Source code for Java-based tests of actors and workflows.
src/test/resources   | Resource files available to Java-based tests.

##### Python library layout

All python code provided with kurator-validation is organized in a single directory tree at `src/main/python`.  This directory tree is structured so that all code is in sub-packages of the `kurator.validation` Python package.  The 

Directory            | Description
-----------------------------------------|------------
kurator/validation/actors      | Python sources for libraries, scripts, and actors.
