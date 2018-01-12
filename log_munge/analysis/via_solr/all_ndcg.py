import requests
import json
import numpy as np

#calculate ndcg

# assumption: clicks indicate relevance judgements 
# assumption: unclicked items are therefore irrelevant
# note: because of the way the API treats filter queries (all refinements but the most-recently
# submitted are treated as filter queries), each combination of queries and
# filters is treated as a distinct query
# from unfiltered searches

class Query:

	SOLR_STUB = "http://144.76.218.178:8989/solr/analytics/select?indent=on&wt=json"

	def __init__(self, query_term, filter_queries, total_results):
		self.query_term = query_term
		self.filter_queries = filter_queries
		self.total_results = total_results
		self.judgements = []
		self.ndcgs = []
		self.avg_ndcg = -1

	def set_results(self, result_count):
		self.results = [0] * result_count

	def add_relevance_judgement(self, index):
		fencepost = index - 1
		self.judgements.append(fencepost)
		self.results[fencepost] = 1

	def calculate_ndcgs(self, clicks):
		for k, v in clicks.items():
			for rank in v:
				ndcg = self.ndcg_at_k(self.judgements, rank)
				self.ndcgs.append(ndcg)

	def calculate_avg_ndcg(self):
		if(len(self.ndcgs) > 0):
			self.avg_ndcg = sum(self.ndcgs) / len(self.ndcgs)

	def do_ndcg(self):
		results = self.query_for_results()
		self.build_relevance_judgements(results)
		unique_clicks = self.collect_unique_clicks(results)
		self.calculate_ndcgs(unique_clicks)
		self.calculate_avg_ndcg()

	def query_for_results(self):
		search_term = "&q=query_term:\"" + self.query_term.replace("\"", "\\\"") + "\""
		filter_terms = ""
		for filter_term in self.filter_queries:
			filter_terms += "&fq=\"" + filter_term + "\""
		rows = "&rows=" + str(self.total_results)
		qry = Query.SOLR_STUB + "&fl=session_id,total_results,rank_position&fq=operation:\"RankedRetrieveRecordInteraction\"" + search_term + filter_terms + rows
		try:
			res = requests.get(qry).json()
		except:
			print("ERROR on query: " + qry)
			res = {}
		return res

	def build_relevance_judgements(self, results):
		positions = []
		lengths = []
		try:
			for doc in results["response"]["docs"]:
				no_error = 1
				lengths.append(doc["total_results"])
				positions.append(doc["rank_position"])
		except KeyError:
			lengths.append(1)
			positions.append(0)
			no_error = 0
		max_length = max(lengths)
		positions = set(positions)
		self.judgements = [0] * max_length
		for position in positions:
			position = position - 1
			if(no_error):
				relevance = 1
			else:
				relevance = 0
			self.judgements[position] = relevance

	def collect_unique_clicks(self, results):
		clicks_by_user = {}
		for doc in results["response"]["docs"]:
			user_id = doc["session_id"]
			rank = doc["rank_position"]
			try:
				if(rank not in clicks_by_user[user_id]):
					clicks_by_user[user_id].append(rank)
			except KeyError:
				clicks_by_user[user_id] = [rank]
		return clicks_by_user

	def output_self(self, file_name):
		msg = self.query_term + "\t" + ",".join(self.filter_queries) + "\t" + str(self.ndcgs) + "\t" + str(self.avg_ndcg) + "\n"
		with open(file_name, 'a') as biglist:
			biglist.write(msg)

	# dcg and ndcg methods simplified from https://gist.github.com/bwhite/3726239

	def dcg_at_k(self, r, k):
	    r = np.asfarray(r)[:k]
	    if r.size:
	    	return np.sum(r / np.log2(np.arange(2, r.size + 2)))
	    return 0.

	def ndcg_at_k(self, r, k):
	    dcg_max = self.dcg_at_k(sorted(r, reverse=True), k)
	    if not dcg_max:
	    	return 0.
	    return self.dcg_at_k(r, k) / dcg_max

	def get_avg_ndcg(self):
		return self.avg_ndcg

	def get_query_term(self):
		return self.query_term

all_queries = "http://144.76.218.178:8989/solr/analytics/select?facet=on&fq=operation:%22RankedRetrieveRecordInteraction%22&indent=on&q=*:*&rows=0&wt=json&facet.field=query_term&facet.limit=-1&facet.mincount=1"
query_terms = []
res = requests.get(all_queries).json()
for qt in res["facet_counts"]["facet_fields"]["query_term"]:
	query_terms.append(qt)
i = 0
step = 10
bare_queries = []
print(str(len(query_terms[::step])))
while i < len(query_terms[::step]):
	query_term = query_terms[i]
	query_term = query_term.replace("\"", "\\\"")
	query_count = query_terms[i + 1]
	solr_qry = "http://144.76.218.178:8989/solr/analytics/select?fl=query_term,filter_term&fq=operation:%22RankedRetrieveRecordInteraction%22&indent=on&wt=json"
	solr_qry += "&q=query_term:\"" + query_term + "\"&rows=" + str(query_count)
	try:
		res = requests.get(solr_qry).json()
		for doc in res["response"]["docs"]:
			qry = doc["query_term"]
			if "filter_term" in doc.keys():
				qry += "=>"
				filter_terms = []
				for filter_term in doc["filter_term"]:
					filter_terms.append(filter_term)
				qry += "|".join(filter_terms)
			qry = qry + "~" + str(query_count)
			if(qry not in bare_queries):
				bare_queries.append(qry)
	except:
		print("ERROR: " + solr_qry)
	i += step

fledged_queries = []
for q in bare_queries:
	(query_bit, count) = q.split("~")
	if("=>" not in query_bit):
		query = query_bit
		filters = []
	else:
		(query, raw_filters) = query_bit.split("=>")
		filters = raw_filters.split("|")
	fledged_query = Query(query, filters, count)
	try:
		fledged_query.do_ndcg()
		fledged_queries.append(fledged_query)
	except:
		pass

overall_avg = 0
for fq in fledged_queries:
	overall_avg += fq.get_avg_ndcg()
	fq.output_self("all_queries.txt");

print("Overall nDCG is " + str(overall_avg / len(fledged_queries)))







