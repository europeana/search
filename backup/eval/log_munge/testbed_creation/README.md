# Query testbed for evaluation

This directory contains the queries to be used for evaluation of Europeana's ranking algorithm(s).

## Criteria for inclusion

Note that all queries are taken from Europeana's query logs, between March and September 2017.

To be included in the query testbed, a query must:

1. Have at least one defined query term (i.e., '\*:\*' queries are excluded)
2. Yield at least ten results in the SERP
3. Have been issued in at least ten different sessions
4. Have yielded at least ten relevance judgements (i.e., clicks)

The reasons for these criteria are outlined in the Query Logs Analysis [README document](https://github.com/europeana/contrib/tree/master/query-logs-analysis).