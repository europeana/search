# this retrieves all query terms that appear in at least ten sessions
# and yield at least ten hits
import requests
import json
import os
import time
import re

SOLR_URI = "http://144.76.218.178:8989/solr/analytics/select?"
SOLR_GET_TERMS = SOLR_URI + "q=query_term%3A*&sort=query_term+asc&wt=json&indent=true&facet=true&facet.field=query_term&fq=operation:RankedRetrieveRecordInteraction&fq=total_results:[10%20TO%20*]"
query_terms = []
query_info = {}

def munge_for_file_name(term):
	token_term = re.sub(r' ', '_', term)
	cleaned_term = re.sub(r'\W', '', token_term)
	shrunk_term = cleaned_term[0:25]
	return shrunk_term + ".txt"

def output_terms(term_hash):
	for k, v in term_hash.items():
		file_name = munge_for_file_name(k)
		with open(os.path.join('query_interactions', file_name), 'w') as snout:
			snout.write(k + "\n")
			for item in v:
				msg = item['timestamp'] + "\t" + item['session_id']  + "\t" + item['filter_term'] + "\t" + item['uri'] + "\t" + item['rank_position'] + "\t" + item['total_results'] + "\n"
				snout.write(msg)

offset = 0
rows = 100

total_query = requests.get(SOLR_GET_TERMS).json()
total_results = int(total_query['response']['numFound'])

results_found = {}
processing_term = ""

while(offset < total_results):
	time.sleep(1)
	paged_query = SOLR_GET_TERMS + "&rows=" + str(rows) + "&start=" + str(offset)
	paged_results = requests.get(paged_query).json()
	docs = paged_results['response']['docs']
	term_hits = []
	for doc in docs:
		qterm = str(doc['query_term'])
		if(qterm != processing_term):
			if(len(term_hits) >= 10):
				results_found[processing_term] = term_hits
			term_hits = []
			processing_term = qterm
		item = {}
		item['query_term'] = qterm
		item['session_id'] = str(doc['session_id'])
		item['timestamp'] = str(doc['timestamp'])
		item['rank_position'] = str(doc['rank_position'])
		item['uri'] = str(doc['uri'])
		item['total_results'] = str(doc['total_results'])
		if('filter_term' in doc.keys()):
			item['filter_term'] = str(doc['filter_term'])
		else:
			item['filter_term'] = str([])
		term_hits.append(item)
	output_terms(results_found)
	results_found = {}
	offset += rows





