# LogsManagement

Basic (and temporal) software to continue the evaluation from logs coming from the ELK stack.

## Input
The logs are assumed to be contained in a folder resulting from applying Tim's code log_extractor.session_extractor and log_extractor.entry_extractor.
This code can be found at /evaluation/log_munge
The resulting folder is called 'entries_by_session'. The path of this folder should be configured in resources/config.properties

## Output
Generates TREC_EVAL files: qrel.txt, with the ground truth from the logs, and res.txt, with the results
If a document is clicked (even if it is clicked only once), it is considered relevant.
Additionally a description of queries and sessions will be printed:
* Queries are grouped if they have the same query keyword, same filters and same number of hits
* Sessions are unique sessions, containing search activities (I register only two, the search and the click of results)
* A query is considered to have 'query keywords' if it is not empty, it does not contain the string 'NO VALUE PROVIDED', or the wildcards '*' or '*:*'
* A filter is considered not empty if the string is not empty
For the ground truth, only queries with keywords and at least one click are considered.

*Important to note:* the source of the search activities logged is still unclear, so in this data is also probably included the data resulting from internal operations (eg. automatic updating of collections) and external crawlers.
