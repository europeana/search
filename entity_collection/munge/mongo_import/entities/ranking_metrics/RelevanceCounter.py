import requests
import os
import math

class RelevanceCounter:
    """
       Calculates the relevance of a given entity, based on two factors:
       Wikidata PageRank and the number of exact-match hits an OR query
       using the entity's various language labels retrieves. Two other factors
       are also available: the number of enrichments using the entity's URL found in
       Europeana datastores; and Wikipedia clickstream popularity.


       In terms of process, this class is very simple: while processing each
       entity, it checks to see whether the above metrics are already stored
       in the relevant sqlite database. If so, it retrieves the results; if not,
       it calculates the Europeana-related metrics (enrichment and term count)
       and inserts these into the database for later retrieval.
   """

    #MOSERVER = 'mongodb:localhost'
    #MOPORT = 27017
    SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0"

    def __init__(self, name):
        import sqlite3 as slt
        import sys, os
        self.name = name
        self.dbpath = os.path.join(os.path.dirname(__file__), 'db', name + ".db")
        self.db = slt.connect(self.dbpath)
        self.penalized_entities = []
        with open(os.path.join(os.path.dirname(__file__), 'resources', 'worst_bets.txt')) as wbets:
            for line in wbets.readlines():
                line = line.strip()
                self.penalized_entities.append(line)

    def normalize_string(self, normanda):
        import re

        normatus = re.sub("[()[]\",]", " ", normanda.strip())
        normatus = re.sub("\s+", " ", normatus)
        normatus = re.sub(" ", "_", normatus)
        return normatus

    def get_raw_relevance_metrics(self, uri, representation):
        csr = self.db.cursor()
        csr.execute("SELECT * FROM hits WHERE id=?", (uri,))
        first_row = csr.fetchone()
        if(first_row is not None):
            (_, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits, pagerank) = first_row
            if(pagerank is None):
                pagerank = 0
        else:
            wikipedia_hits = -1
            europeana_enrichment_hits = self.get_enrichment_count(uri)
            europeana_string_hits = self.get_label_count(representation)
            pagerank = 0
            z = csr.execute("INSERT INTO hits(id, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits, pagerank) VALUES (?, ?, ?, ?, ?)", (uri, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits, pagerank))
            self.db.commit()
        metrics = {
            "wikipedia_hits" : wikipedia_hits,
            "europeana_enrichment_hits" : europeana_enrichment_hits,
            "europeana_string_hits" : europeana_string_hits,
            "pagerank" : pagerank
        }
        return metrics

    def get_enrichment_count(self, uri):
        qry = RelevanceCounter.SOLR_URI + "?q=\"" + uri + "\""
        res = requests.get(qry)
        try:
            return res.json()['response']['numFound']
        except:
            return 0

    def get_label_count(self, representation):
        all_labels = []
        [all_labels.extend(l) for l in representation['prefLabel'].values()]
        qry_labels = ["\"" + label + "\"" for label in all_labels]
        qs = " OR ".join(qry_labels)
        qry = RelevanceCounter.SOLR_URI + "&q=" + qs
        res = requests.get(qry)
        try:
            return res.json()['response']['numFound']
        except:
            return 0

    def calculate_relevance_score(self, uri, pagerank, eu_doc_count, eu_term_count):
        if(pagerank is None): pagerank = 0
        pagerank = pagerank + 1 # eliminate values > 1
        # two effects: pagerank only boosts values
        # old: no europeana hits drops relevance to zero
        # old: no pagerank value leaves relevance as europeana hits
        # new: no enrichments for this entity found -> use term hits
        # new: use 1+ln(term hits) to reduce the effect of false positives (the search is ambiguous)
        relevance = 0;
        #for organizations the default enrichment count is set to 1
        if(eu_doc_count > 1):
            relevance = eu_doc_count * pagerank
        elif(eu_term_count > 0):
            relevance = (1 + math.log(eu_term_count, 10)) * pagerank   
        else:    
            return 0
        
        deprecation_factor = 1
        if(id in self.penalized_entities):
            deprecation_factor = 0.5
        normed_relevance = math.floor(math.log(relevance) * 10000) * deprecation_factor
        return normed_relevance

class AgentRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'agent')

class ConceptRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'concept')

class PlaceRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'place')

class OrganizationRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'organization')

    def get_enrichment_count(self, uri):
        #TODO add proper implementation of counting items for organizations
        print("return default enrichment count 1 for organization: " + uri)
        return 1

    def get_label_count(self, representation):
        #TODO add proper implementation of counting enrichments with organizations
        print("return default value for label count: 1")
        return 1

