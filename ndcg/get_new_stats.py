from collections import namedtuple
from copy import deepcopy
import pymongo
import requests
import numpy as np

SOLR = "http://sol1.eanadev.org:9191/solr/search_1/search"
MONGO = "mongodb://localhost"
all_queries = []

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
        num_hits = len(self.previous_hits)
        solr_qry = SOLR + "?wt=json&q=" + self.query + "&fl=europeana_id&rows=" + str(num_hits)
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

    def serialize_as_dict(self):
        # TODO: there must be a more pythonic way to do this
        self_dict = {}
        self_dict['query'] = self.query
        self_dict['previous_hit_count'] = self.previous_count
        self_dict['current_hit_count'] = self.current_count
        self_dict['previous_rankings'] = []
        for h in self.previous_hits:
            self_dict['previous_rankings'].append(h._asdict())
        self_dict['current_rankings'] = []
        for i in self.rankings:
            self_dict['current_rankings'].append(i._asdict())
        return self_dict

class MetricsCalculator:

    # from https://gist.github.com/bwhite/3726239

    def __init__(self):
        self.cl = pymongo.MongoClient(MONGO, 27017)

    def dcg_at_k(self, r, k, method=0):
        """Score is discounted cumulative gain (dcg)
        Relevance is positive real values.  Can use binary
        as the previous methods.
        Example from
        http://www.stanford.edu/class/cs276/handouts/EvaluationNew-handout-6-per.pdf
        >>> r = [3, 2, 3, 0, 0, 1, 2, 2, 3, 0]
        >>> dcg_at_k(r, 1)
        3.0
        >>> dcg_at_k(r, 1, method=1)
        3.0
        >>> dcg_at_k(r, 2)
        5.0
        >>> dcg_at_k(r, 2, method=1)
        4.2618595071429155
        >>> dcg_at_k(r, 10)
        9.6051177391888114
        >>> dcg_at_k(r, 11)
        9.6051177391888114
        Args:
            r: Relevance scores (list or numpy) in rank order
                (first element is the first item)
            k: Number of results to consider
            method: If 0 then weights are [1.0, 1.0, 0.6309, 0.5, 0.4307, ...]
                    If 1 then weights are [1.0, 0.6309, 0.5, 0.4307, ...]
        Returns:
            Discounted cumulative gain
        """
        r = np.asfarray(r)[:k]
        if r.size:
            if method == 0:
                return r[0] + np.sum(r[1:] / np.log2(np.arange(2, r.size + 1)))
            elif method == 1:
                return np.sum(r / np.log2(np.arange(2, r.size + 2)))
            else:
                raise ValueError('method must be 0 or 1.')
        return 0.

    def calc_ndcg_on_each(self, collection_name):
        # we eliminate all searches that no longer return any hits because of collections having
        # been removed
        res = self.cl.europeana[collection_name].find({ 'current_hit_count' : { "$gt": 0 }})
        for record in res:
            id = record['_id']
            # relevance is currently a float; we need an integer for normalisation to work correctly
            previous_ranks = [int(float(hit['relevance']) * 1000) for hit in record['previous_rankings']]
            current_ranks = [int(float(hit['relevance']) * 1000) for hit in record['current_rankings']]
            dcg = self.dcg_at_k(current_ranks, len(current_ranks), 1)
            # we treat the list of all clicked documents from the 904Labs logs as the highest attainable DCG
            max_dcg = self.dcg_at_k(sorted(previous_ranks, reverse=True), len(previous_ranks), 1)
            ndcg = 0
            if max_dcg:
                ndcg = dcg / max_dcg
            self.cl.europeana[collection_name].update({"_id" : id }, { "$set" : {"new_ndcg" : ndcg } })
            print(ndcg)

class StatsHarvester():

    def __init__(self, collection):
        self.cl = pymongo.MongoClient(MONGO, 27017)
        self.collection = collection

    def get_stats(self):
        self.get_old_stats()
        self.get_new_stats()

    def get_old_stats(self):
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

    def get_new_stats(self):
        for query in all_queries:
            query.update_stats()
            id = self.cl.europeana[self.collection].insert_one(query.serialize_as_dict()).inserted_id


sh = StatsHarvester('bm25f')
sh.get_stats()

mc = MetricsCalculator()
mc.calc_ndcg_on_each('bm25f')