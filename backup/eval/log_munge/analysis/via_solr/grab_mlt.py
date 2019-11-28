import requests
import json
import collections
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
from time import sleep
	

# what needs to happen:
# 1. get all record-retrieval entries
# 2. get record retrieved and session id
# 3. query similar.json endpoint 
# 4. store these in a list
# 5. loop through the list, checking to see if the session id and this record are found
# 6. if so, annotate
# 7. divide number with clicked over total to get percentage of use
# 8. calculate ndcg relative to each list

class MLTCandidate:

	ES_URL = "http://elasticsearch2.eanadev.org:9200"

	def __init__(self, session_id, record_id):
		self.session_id = session_id
		self.record_id = "/record/" + record_id.split("/record/")[1]
		self.similar_items = collections.OrderedDict()
		self.judgements = [0, 0, 0, 0]
		self.mlt_clicked = False
		self.ndcgs = []
		self.avg_ndcg = 0

	def get_language(self):
		lang_string = "[200] GET /portal/*/search"
		es_instance = connections.create_connection(hosts=[MLTCandidate.ES_URL], timeout=60)
		initsearch = Search(using=es_instance, index="logstash-*")
		lang = Q('bool', must=[Q('match', session_id=self.session_id), Q('match', message=lang_string)])
		langsearch = initsearch.query(lang)
		response = langsearch.execute()
		for hit in response:
			msg = hit["message"]
			lang_code = msg.split("/")[2]
			self.lang_code = lang_code
			return
		self.lang_code = "en"

	def populate_similar_items(self):
		uri = "https://www.europeana.eu/portal/" + self.lang_code + self.record_id + "/similar.json"
		try:
			res = requests.get(uri).json()
			for doc in res["documents"]:
				self.similar_items[doc["url"]] = False
		except Exception as e:
			print("Exception on: " + str(e))
		
	def query_for_similar_items(self):
		count = 0
		for sim_item in self.similar_items:
			fulltext = "[200] GET " + sim_item
			es_instance = connections.create_connection(hosts=[MLTCandidate.ES_URL], timeout=60)
			initsearch = Search(using=es_instance, index="logstash-*")
			session_search = initsearch.query(Match(session_id={ "query" : self.session_id}))
			sim_search = session_search.query(Match(message={ "query" : fulltext, "type" : "phrase"}))
			response = sim_search.execute()
			if(len(response) > 0):
				self.similar_items[sim_item] = True
				self.judgements[count] = 1
			count += 1

	# TODO: modularise nDCG functions

	def dcg_at_k(self, r, k):
	    r = np.asfarray(r)[:k]
	    if r.size:
	    	return np.sum(r / np.log2(np.arange(2, r.size + 2)))
	    return 0.

	def ndcg_at_k(self, k):
	    dcg_max = self.dcg_at_k(sorted(self.judgements, reverse=True), k)
	    if not dcg_max:
	        return 0.
	    return self.dcg_at_k(self.judgements, k) / dcg_max
	
	def sim_item_clicked(self):
		clicked = False
		for judgement in self.judgements:
			if(judgement > 0):
				clicked = True
		return clicked

	def calculate_ndcg(self):
		for k in range(len(self.judgements)):
			if(k == 1):
				self.ndcgs.append(self.ndcg_at_k(k))
		self.avg_ndcg = sum(self.ndcgs) / len(self.ndcgs)

	def get_avg_ndcg(self):
		return self.avg_ndcg

solr_stub = "http://144.76.218.178:8989/solr/analytics/select?fl=session_id,uri&fq=operation:%22RankedRetrieveRecordInteraction%22&indent=on&q=*:*&wt=json"
total_count = requests.get(solr_stub).json()["response"]["numFound"]
rows = 10
page = 100
offset = 0
mlt_candidates = []
while offset <= total_count:
	solr_req = solr_stub + "&start=" + str(offset) + "&rows=" + str(rows)
	res = requests.get(solr_req).json()
	try:
		for doc in res["response"]["docs"]:
			session_id = doc["session_id"]
			record_id = doc["uri"]
			mlt_candidate = MLTCandidate(session_id, record_id)
			mlt_candidates.append(mlt_candidate)
	except:
		pass
	offset += page
	if(offset % 1000 == 0):
		print(str(offset) + " of " + str(total_count) + " processed")

clicked_mlt_candidates = []
for mc in mlt_candidates:
	mc.get_language()
	mc.populate_similar_items()
	mc.query_for_similar_items()
	if(mc.sim_item_clicked()):
		clicked_mlt_candidates.append(mc)
		mc.calculate_ndcg()

percentage_clicked = len(clicked_mlt_candidates) / len(mlt_candidates)
ndcgs = []
for clandidate in clicked_mlt_candidates:
	ndcgs.append(clandidate.get_avg_ndcg())
print(ndcgs)
total_avg_ndcg = sum(ndcgs) / len(ndcgs)

print("Percentage clicked: " + str(percentage_clicked))
print("Avg nDCG: " + str(total_avg_ndcg))


