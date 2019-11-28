# LogsManagement

Basic (and temporal) software to continue the evaluation from logs coming from the ELK stack.

It takes as input the log information from a specific period of time, extracts the queries issued and the documents clicked and output general stats and the required information to evaluate the effectiveness with [TREC_EVAL](https://github.com/usnistgov/trec_eval).
For the analysis, queries are aggregated if they have the same query keyword, same filters and same number of hits. Only queries with at least one click are considered in the ground truth (qrel files). If a document is clicked (even if it is clicked only once), it is considered relevant.

## Input
The logs are assumed to be contained in a folder resulting from applying Tim's code log_extractor.session_extractor and log_extractor.entry_extractor.
This code can be found at /evaluation/log_munge
The resulting folder is called 'entries_by_session'. The path of this folder should be configured in resources/config.properties

## Configuration (resources/config.properties)
path=[path of the folder 'entries_by_session' where the log information by session is stored] 

## Output
Generates TREC_EVAL files: qrel_[x].txt, with the ground truth from the logs, and res_[x].txt, with the results

The specific output files generated are:
* qrel_all.txt and res_all.txt: input files for TREC_EVAL with all the queries
* qrel_filters.txt and res_filters.txt: input files for TREC_EVAL with all the queries which contain filters (or where the query is only a wildcard)
* qrel_keywords.txt and res_keywords.txt: input files for TREC_EVAL with all the queries which contains keywords (not only filters and not only wildcards)

Additionally stats regarding the queries will be printed in the files stats_all.txt, stats_filters.txt and stats_keywords.txt


*Important to note:* the source of the search activities logged is still unclear, so in this data is also probably included the data resulting from internal operations (eg. automatic updating of collections) and external crawlers.
