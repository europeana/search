from collections import namedtuple
from copy import deepcopy
import pymongo
import requests

SOLR = "http://sol1.eanadev.org:9191/solr/search_1/search"
MONGO = "mongodb://localhost"
all_queries = []

# first we need to populate our query map

class Query:

    def __init__(self, query, result_id, raw_relevance):
        self.Hit = namedtuple('Hit', 'identifier relevance')
        self.query = query
        self.previous_hits = []
        self.previous_count = 0
        self.current_count = 0
        self.rankings = []
        hit = self.Hit(result_id, raw_relevance)
        self.previous_hits.append(hit)
        self.query_for_previous_count()

    def add_hit(self, result_id, raw_relevance):
        hit = self.Hit(result_id, raw_relevance)
        self.previous_hits.append(hit)

    def query_for_previous_count(self):
        client = pymongo.MongoClient(MONGO, 27017)
        self.previous_count = client.europeana.logs.find_one({ 'q' : self.query})['numfound']

    def update_stats(self):
        solr_qry = SOLR + "?wt=json&q=" + self.query + "&fl=europeana_id"
        resp = requests.get(solr_qry).json()
        self.current_count = resp['response']['numFound']
        for doc in resp['response']['docs']:
            id = doc['europeana_id']
            prev_hit = self.find_previous_hit(id)
            self.rankings.append(prev_hit)

    def find_previous_hit(self, record_id):
        for hit in self.previous_hits:
            if record_id == hit[0]:
                new_record = deepcopy(hit)
                return new_record
        return self.Hit('None', 0)

with open('queries.tsv', 'r') as queries:
    current_term = ""
    for line in queries:
        (_,_,term,_,_,_,id,relcalc,_) = line.split('\t')
        if(term != current_term):
            qry = Query(term, id, relcalc)
            all_queries.append(qry)
            current_term = term
        else:
            all_queries[-1].add_hit(id, relcalc)
    print(all_queries)

for query in all_queries:
    print('query is ' + query.query)
    query.update_stats()