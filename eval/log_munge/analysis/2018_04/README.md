# Metrics Report: Jan - April 2015

This directory contains the information used to generate the usage reports for the first quarter of 2018.

THe procedure used was:

1.  Harvest all sessions for the period from our ELK logs
2.  Load the query information for these sessions into a Solr 4.10.4 instance
3.  Perform queries against the Solr index for simple measures such as filter usage.
4.  Run scripts for more complex metrics such as nDCG

## Description of contents

1.  `conf`: contains the bespoke configuration files for the Solr instance
2.  `entries_by_session` contains the sessionified query logs
3.  `entries_by_session/as_xml` are these same files, converted to Solr XML
4.  `all_ndcg.py` queries Solr and calculates an overall nDCG score
5.  `grab_mlt.py` queries Solr and calculates the nDCG score for MLT items
