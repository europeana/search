# Newspapers

Software to index the newspaper collection from the zip files containing the XML information of the full-text obtained by the API team. It involves a merge between that information and the  metadata contained currently in the metadata collection. A validation process can be run (in config.properties) in order to check that the records generated contain exactly the same metadata.

## Configuration (resources/config.properties)
* solrindex=[URL of the Solr collection where the records containing metadata and fulltext will be indexed]
* solrindextype=[Type of SolrClient where the records will be indexed: single, concurrent, cloud. IT DOES NOT HAVE ANY IMPACT FOR THE MOMENT]
* datafolder=[path to the zip files where the XML files are stored]
* solrquery=[URL of the Solr endpoint from where the metadata will be obtained]
* solrquery_collection=[name of the collection used to get the metadata]
* threads=[number of threads to be used]
* buffersize=[batch of documents to index at once]
* process=[Indexing or validating (check metadata is same as original) process: validate, index]
* nrecords=[Number of records to validate]

## Output
Records indexed in the Solr collection indicated.