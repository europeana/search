import requests
import json
import time
import random

api_uri = "https://www.europeana.eu/api/v2/search.json?wskey=api2demo&profile=minimal&rows=96"
solr_uri = "http://sol☃.eanadev.org:9191/solr/search_production_publish_1/search?wt=json&fl=title,europeana_id&rows=96"

api_responses = {}
solr_responses = {}

query_reps = 10

class QueryResponse:

	def __init__(self, repetition, item_count):
		self.repetition = repetition
		self.item_count = item_count
		self.items = []

	def add_item(self, item_id, title):
		as_tuple = (item_id, title)
		self.items.append(as_tuple)

	def output_self(self):
		position = str(self.repetition)
		results = str(self.item_count)
		msg = position + "\t" + results + "\t" + "\t".join(str(item) for item in self.items)
		return msg

def build_query(entry, target, iteration):
	offset = "96" if iteration % 2 == 1 else "0"
	offset_qs = "&start=" + offset
	qs = "q" if target != "api" else "query"
	fq = "fq" if target != "api" else "qf"
	try:
		(query, fqs) = entry.split("\t")
		filters = ("&").join(fq + "=" + f for f in fqs.split(","))
		qs = qs + "=" + query + "&" + filters
	except ValueError:
		qs = qs + "=" + entry.strip()
	qs += offset_qs
	return qs

all_queries = []
with open("queries.tsv") as qt:
	for line in qt.readlines():
		all_queries.append(line.strip())

for i in range(0, query_reps):
	for now_query in all_queries:
		time.sleep(240)
		qstring = build_query(now_query, "api", i)
		apiq = api_uri + "&" + qstring
		try:
			apir = requests.get(apiq).json()
			item_count = apir['totalResults']
			qr = QueryResponse(i, item_count)
			for item in apir['items']:
				myid = item['id']
				title = " ".join(item['title'])
				qr.add_item(myid, title)
			try:
				api_responses[apiq].append(qr)
			except KeyError:
				api_responses[apiq] = [qr]
			sstring = build_query(now_query, "solr", i)
			server = str(random.randint(7,12))
			solrq = solr_uri.replace("☃", server) + "&" + sstring
			print(solrq)
		except:
			pass
		solrr = requests.get(solrq).json()
		try:
			sitem_count = solrr['response']['numFound']
			sqr = QueryResponse(i, sitem_count)
			for doc in solrr['response']['docs']:
				eid = doc['europeana_id']
				title = " ".join(doc['title'])
				sqr.add_item(eid, title)
				solr_key = solrq.replace(server, "☃", 1)
			try:
				solr_responses[solr_key].append(sqr)
			except KeyError:
				solr_responses[solr_key] = [sqr]
		except:
			pass

with open('api_results.tsv', 'w') as ar:
	for query, responses in api_responses.items():
		for response in responses:
			as_string = response.output_self()
			msg = query + "\t" + as_string + "\n"
			ar.write(msg)
		ar.write("\n")

with open('solr_results.tsv', 'w') as sr:
	for query, responses in solr_responses.items():
		for response in responses:
			as_string = response.output_self()
			msg = query + "\t" + as_string + "\n"
			sr.write(msg)
		sr.write("\n")



		
