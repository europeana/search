# Consistency testing

The purpose of these files is to investigate issues relating to [https://europeana.atlassian.net/browse/EA-960](API ticket 960): Inconsistent search results for consistent queries.

The approach here uses four files:

1. `queries.tsv`, a tab-separated list of queries with their (comma-separated) filter-queries.
1. `api_results.tsv`, a tab-separated list of results from the API 
1. `solr_results.tsv`, a tab-separated list of results from Solr (to determine at which layer the difficulty is occurring)
1. `fire.py`, the Python 3 file that fires the queries listed in `queries.tsv` against the API and Solr and writes the results to the relevant output file

### TODO: Determine and document format for results files