# Test scripts

This directory is for tests of the Entity Collection as it exists in Solr.

Note that this directory has a package/module structure. To run the tests, it will be necessary to

* cd to the `mongo_import` directory
* start a REPL by entering `python3` at the command prompt
* `from tests import [package]`

You will then be able to invoke whatever functions are required within that package. For example, to run all the tests found in `mdb2solr.py`:

* `from tests import mdb2solr as m2s`
* `m2s.run_test_suite()`

## import_tests.py

This file contains objects and functions used to test the fidelity of the scripts that transform our Mongo records into Solr documents (i.e., that no 'noise' is added to, or information lost from, the files), and the completeness of the import (that no records are lost in the process). The tests do not constitute a validation of the data itself; they simply ensure that the output is correct given the input.

Most of the necessary documentation is given inline in the file itself. One general point, however, should be noted: many functions take a pair of boolean arguments, `suppress_stdout` and `log_to_file`. By default the script will write any output to STDOUT; setting `suppress_stdout=True` disables this. Setting `log_to_file=True` causes any output additionally to be written to a log file in the `../logs/import_tests` directory.

In addition to the tests, the file contains a couple of reporting functions. The first of these, `report_filecount_discrepancy`, writes the ID of any entity missing from the Solr core but found in Mongo to a logfile in the `../logs/import_tests` directory. The second, `report_missing_fields`, writes the ID of any entity in Solr missing the passed field, to a logfile in the same directory.
