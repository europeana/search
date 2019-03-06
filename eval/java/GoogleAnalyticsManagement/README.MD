# GoogleAnalyticsManagement

Software to generate a sample of queries and additional information from Google Analytics that can help to evaluate the Entity Collection coverage (how many queries are related to entities contained in our Entity Collection).

It connects to the www.europeana.eu Google Analytics account via the Google Analytics Report API, and get a sample of queries issued for a specific period of time. For each query, the Entity Collection is checked (directly in Solr) to indicate if there exist one entity where that query is part of its labels or part of the text field. 

*Note:* Before the sampling, the queries are filtered to only those with less than 11 searches, containing only letters, with more than 2 characters, and not including logical operators (AND, OR).

## Configuration (resources/config.properties)
* solr_entity=[URL of Solr Entity Collection]
* start_date=[YYYY-MM-DD]
* end_date=[YYYY-MM-DD] 
* sample_size=[total number of queries as output]
* ga_sampling=[sampling made by Google Analytics when downloading the data. Options: SMALL, LARGE and DEFAULT]
* gakey=[path to Google Analytics credentials (json file)] 

## Output
File 'query_sample.csv', with the following information separated by tabs:
* Query
* Portal or thematic collection from were the query was issued
* Language of the web page from were the query was issued
* Types of entities were that query was found in the label field of the Entity Collection
* Types of entities were that query was found in the text field of the Entity Collection
* Types of entities were the tokens of the query were found in the label field of the Entity Collection
* Types of entities were the tokens of the query were found in the text field of the Entity Collection