import requests
import json
import sqlite3
import urllib3
from pymongo import MongoClient
from entities import HarvesterConfig
from urllib.parse import quote

# purpose of script is to populate the ranking metrics for Organizations
# Right now we need URI hits, term hits, and PageRank
# (Wikipedia hits are now deprecated as a ranking sigal)

# first, we need to grab all Organization identifiers from Mongo, as well as their
# @en labels 

org_records = []

class OrgRecord:

	def __init__(self, uri, label):
		self.id = uri
		self.wikidata_id = None
		self.def_label = label
		self.uri_hits = 0
		self.term_hits = 0
		self.wpd_hits = 0
		self.pagerank = 0.0
		self.all_labels = []


def	extract_def_label(org):	
	#en_label = org['representation']['prefLabel']['en'][0]
	label = 'Not available'
	pref_label = org['representation']['prefLabel']
	country_key = None
	if('edmCountry' in org.keys()):
		country_key = org['edmCountry'].lower()
		
	if('en' in pref_label.keys()):
		label = pref_label['en'][0]
	elif((country_key is not None) and (country_key in pref_label.keys())):
		label = pref_label[country_key][0]
	else:
		label = next(iter(pref_label.values()))[0]
	return label
		

def extract_all_labels (org):
	lbls = []
	#TODO filter to use only labels in European languages (use boolean method param)
	for lv in org['representation']['prefLabel']:
		[lbls.append(lbl) for lbl in org['representation']['prefLabel'][lv]]
	#pref labels are not mandatory
	if('altLabel' in org['representation'].keys()):
		for lv in org['representation']['altLabel']:
			try:
				[lbls.append(lbl) for lbl in org['representation']['altLabel'][lv]]
			except KeyError:
				pass	
	return lbls		

def extract_wikidata_identifier(org):
	wikidata_id = None
	WIKIDATA_PREFFIX = 'http://www.wikidata.org/entity/'
			
	if('owlSameAs' in org['representation'].keys()):
		for uri in org['representation']['owlSameAs']:
			if(uri.startswith(WIKIDATA_PREFFIX)):
				wikidata_id = str(uri).replace(WIKIDATA_PREFFIX, '')
				print("has wikidata identifier: " + wikidata_id)
				break
	return wikidata_id

def search_wikidata_id(org):
	lbl = org.def_label
	#TODO expand to use EU labels 
	now_query = wikidata_query.replace('XXXXX', lbl)
	wikidata_req = wikidata_endpoint_url + now_query
	as_json = requests.get(wikidata_req).json()
	wikidata_id = as_json['results']['bindings'][0]['item']['value'].split("/")[-1]
	return wikidata_id

def get_page_rank(wikidata_id, all_pageranks):
	try:
		pagerank = float(all_pageranks[wikidata_id].strip())
		#print("found wikidata page rank for identifier:" + wikidata_id)			
	except (IndexError, KeyError, ValueError):
		#response parsing or value retrieval errors
		print("No page rank found for identifier:" + wikidata_id)
		pagerank = 0.0
	return pagerank

def build_term_hits_query(lbls):
	fielded_query = "PROVIDER:\"XXXXX\" OR DATA_PROVIDER:\"XXXXX\" OR provider_aggregation_edm_intermediateProvider: \"XXXXX\""
	qrs = []
	for lbl in lbls:
		fq = fielded_query.replace('XXXXX', lbl)
		qrs.append(quote(fq))
	fielded_query = "(" + " OR ".join(qrs) + ")"
	term_hits_query = solr_query.replace('XXXXX', fielded_query)
	#print(term_hits_query)
	return term_hits_query

def compute_term_hits(lbls):	
	term_hits_query = build_term_hits_query(lbls)
	try:
		th_as_json = requests.get(term_hits_query).json()
		term_hits = th_as_json['response']['numFound']
	except (ValueError, KeyError):
		#response parsing or retrieval errors
		#TODO: fix too long queries issue
		#print("cannot parse response for query: ")
		#print(term_hits_query)
		if(len(lbls) > 10):
			try:
				term_hits_query = build_term_hits_query(lbls[0:10])
				th_as_json = requests.get(term_hits_query).json()
				term_hits = th_as_json['response']['numFound']
			except (ValueError, KeyError):
				term_hits = 0	
		else:	
			print("cannot get term hits with query: " + term_hits_query)
			term_hits = 0
	
	return term_hits

def compute_enrichment_hits(orgid):
	enrich_hits_query = solr_query.replace('XXXXX', "'" + orgid + "'")
	enrich_as_json = requests.get(enrich_hits_query).json()
	enrich_hits = enrich_as_json['response']['numFound']
	return enrich_hits

def store_metrics(org_records): 	
	conn = sqlite3.connect("../db/organization.db")
	csr = conn.cursor()
	for orgr in org_records: #TODO switch to insert or update
		vals = [str("\"" + orgr.id + "\""), str(orgr.wpd_hits), str(orgr.uri_hits), str(orgr.term_hits), str(orgr.pagerank)]
		instatement = "INSERT OR REPLACE INTO hits VALUES(" + ",".join(vals) + ")"
		print(instatement)
		try:
			csr.execute(instatement)
		except sqlite3.IntegrityError:
			# if hit already registered print()
			pass
	conn.commit()

####  start processing
#read organizations from enrichment database
config = HarvesterConfig.HarvesterConfig()
org_mongo = MongoClient(config.get_mongo_host('organizations'), config.get_mongo_port())
orgs = org_mongo.annocultor_db.TermList.find({ "entityType" : "OrganizationImpl"})

#create OrgRecords
wkdt_identifiers = []
for org in orgs:
	org_id = org['codeUri']
	label = extract_def_label(org) 		
	o = OrgRecord(org_id, label)
	o.wikidata_id = extract_wikidata_identifier(org)
	if(o.wikidata_id is not None):
		wkdt_identifiers.append(o.wikidata_id)
	o.all_labels = extract_all_labels(org)
	org_records.append(o)

PR_URI_PREFIX = "http://wikidata.dbpedia.org/resource/"		
pageranks = {}
	
# process pagerank file, grab relevant items
with open('wd_pr_ultimate.tsv') as ult:
	for line in ult.readlines():
		(identifier, pr) = line.split("\t")
		wkdt_identifier = identifier.replace(PR_URI_PREFIX, '')
		#keep in memory only the EC organizations
		if(wkdt_identifier in wkdt_identifiers):
			pageranks[wkdt_identifier] = pr		

# fetch metrics into OrgRecord
wikidata_endpoint_url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql?format=json&query="
wikidata_query = "SELECT ?item WHERE { ?item rdfs:label|skos:altLabel 'XXXXX'@en. } limit 1"
solr_query = config.get_relevance_solr() + "/select?wt=json&q=XXXXX"
for orgr in org_records:
	if(orgr.wikidata_id is not None):
		orgr.pagerank = get_page_rank(orgr.wikidata_id, pageranks)
	else:
		orgr.pagerank = 0.0
	#all organizations are known and have at least one record, when enrichment is complete the correct values will be used automatically 
	orgr.uri_hits = max(compute_enrichment_hits(orgr.id), 1) 
	orgr.term_hits = compute_term_hits(orgr.all_labels)

#finally store metrics to database
store_metrics(org_records)

