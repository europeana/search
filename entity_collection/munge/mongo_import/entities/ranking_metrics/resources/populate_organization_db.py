import requests
import json
import sqlite3
from pymongo import MongoClient

# purpose of script is to populate the ranking metrics for Organizations
# Right now we need URI hits, term hits, and PageRank
# (Wikipedia hits are now deprecated as a ranking sigal)

# first, we need to grab all Organization identifiers from Mongo, as well as their
# @en labels 

org_records = []

class OrgRecord:

	def __init__(self, id, label):
		self.id = id
		self.en_label = label
		self.uri_hits = 0
		self.term_hits = 0
		self.wpd_hits = 0
		self.pagerank = 0
		self.all_labels = []

org_mongo = MongoClient("mongodb://metis-storage.eanadev.org", 27017)
orgs = org_mongo.annocultor_db.TermList.find({ "entityType" : "OrganizationImpl"})
for org in orgs:
	org_id = org['codeUri']
	try:
		en_label = org['representation']['prefLabel']['en'][0]
		o = OrgRecord(org_id, en_label)
		lbls = []
		for lv in org['representation']['prefLabel']:
			[lbls.append(lbl) for lbl in org['representation']['prefLabel'][lv]]
		for lv in org['representation']['altLabel']:
			[lbls.append(lbl) for lbl in org['representation']['altLabel'][lv]]
		o.all_labels = lbls
		org_records.append(o)
	except KeyError:
		pass

# first, lets get pagerank stats
# first step: get the wikidata identifiers

wikidata_endpoint_url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?format=json&query="
wikidata_query = "SELECT ?item WHERE { ?item rdfs:label|skos:altLabel 'XXXXX'@en. } limit 1"
solr_query = "http://sol7.eanadev.org:9191/solr/search_production_publish_1/select?wt=json&q=XXXXX"
all_pageranks = {}
with open('wd_pr_ultimate.tsv') as ult:
	for line in ult.readlines():
		(identifier, pr) = line.split("\t")
		all_pageranks[identifier] = pr

for orgr in org_records:
	orgid = orgr.id
	lbl = orgr.en_label
	now_query = wikidata_query.replace('XXXXX', lbl)
	wikidata_req = wikidata_endpoint_url + now_query
	as_json = requests.get(wikidata_req).json()
	try:
		wikidata_id = as_json['results']['bindings'][0]['item']['value'].split("/")[-1]
		coref = "http://wikidata.dbpedia.org/resource/" + wikidata_id
		pagerank = all_pageranks[coref].strip()
	except IndexError:
		pagerank = 0
	orgr.pagerank = pagerank
	enrich_hits_query = solr_query.replace('XXXXX', "'" + orgid + "'")
	enrich_as_json = requests.get(enrich_hits_query).json()
	enrich_hits = enrich_as_json['response']['numFound']
	orgr.uri_hits = enrich_hits
	lbls = orgr.all_labels
	qrs = []
	fielded_query = "PROVIDER:\"XXXXX\" OR DATA_PROVIDER:\"XXXXX\""
	for lbl in lbls:
		fq = fielded_query.replace('XXXXX', lbl)
		qrs.append(fq)
	fielded_query = "(" + " OR ".join(qrs) + ")"
	term_hits_query = solr_query.replace('XXXXX', fielded_query)
	th_as_json = requests.get(term_hits_query).json()
	term_hits = th_as_json['response']['numFound']
	orgr.term_hits = term_hits

conn = sqlite3.connect("../db/organization.db")
csr = conn.cursor()
for orgr in org_records:
	vals = [str("\"" + orgr.id + "\""), str(orgr.wpd_hits), str(orgr.uri_hits), str(orgr.term_hits), str(orgr.pagerank)]
	instatement = "INSERT INTO hits VALUES(" + ",".join(vals) + ")"
	print(instatement)
	try:
		csr.execute(instatement)
	except sqlite3.IntegrityError:
		# if hit already registered
		pass
conn.commit()

