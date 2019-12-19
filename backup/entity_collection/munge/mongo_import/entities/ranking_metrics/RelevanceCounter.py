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
    #SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0"

    METRIC_PAGERANK = 'pagerank'
    METRIC_ENRICHMENT_HITS = 'europeana_enrichment_hits'
    METRIC_TERM_HITS = 'europeana_string_hits'
    AGENT = 'agent'
    PLACE = 'place'
    CONCEPT = 'concept'
    ORGANIZATION = 'organization'
    
    METRIC_MAX_VALS = {
        METRIC_PAGERANK : {
            AGENT : 1204,
            PLACE : 24772,
            CONCEPT : 4055,
            ORGANIZATION : 115
            },
        METRIC_ENRICHMENT_HITS : {
            AGENT : 40953,
            PLACE : 3634922,
            CONCEPT : 3305389,
            ORGANIZATION : 1
            },
        METRIC_TERM_HITS : {
            AGENT : 2399975,
            PLACE : 13850981,
            CONCEPT : 6757400,
            ORGANIZATION : 6952064
            }
        }
    
    METRIC_TRUST = {
        METRIC_PAGERANK : 10,
        METRIC_ENRICHMENT_HITS : 2,
        METRIC_TERM_HITS : 1
    }
    
    RANGE_EXTENSION_FACTOR = 10000
     
    def __init__(self, name):
        import sqlite3 as slt
        import HarvesterConfig
        self.config = HarvesterConfig.HarvesterConfig()
        
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
            csr.execute("INSERT INTO hits(id, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits, pagerank) VALUES (?, ?, ?, ?, ?)", (uri, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits, pagerank))
            self.db.commit()
        metrics = {
            "wikipedia_hits" : wikipedia_hits,
            "europeana_enrichment_hits" : europeana_enrichment_hits,
            "europeana_string_hits" : europeana_string_hits,
            "pagerank" : pagerank
        }
        return metrics

    def get_max_metrics(self):
        csr = self.db.cursor()
        csr.execute("SELECT MAX(europeana_enrichment_hits) as meeh, MAX(europeana_string_hits) as mesh, MAX(pagerank) as mpr, MAX(wikipedia_hits) mwph FROM hits")
        first_row = csr.fetchone()
        if(first_row is not None):
            (max_eeh, max_esh, max_pr, max_wphs) = first_row
        
        metrics = {
            "max_enrichment_hits" : max_eeh,
            "max_europeana_string_hits" : max_esh,
            "max_page_rank" : max_pr,
            "max_wikipedia_hits" : max_wphs
        }
        return metrics

    def get_max_pagerank(self):
        csr = self.db.cursor()
        csr.execute("SELECT id, pagerank FROM hits where pagerank = (select max(pagerank) from hits)")
        first_row = csr.fetchone()
        if(first_row is not None):
            (entity_id, max_pr) = first_row
        metrics = {
            "id" : entity_id,
            "max_page_rank" : max_pr,
        }
        return metrics
    
    def get_enrichment_count(self, uri):
        qry = self.config.get_relevance_solr() + "&q=\"" + uri + "\""
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
        qry = self.config.get_relevance_solr() + "&q=" + qs
        res = requests.get(qry)
        try:
            return res.json()['response']['numFound']
        except:
            return 0

    def calculate_relevance_score(self, uri, pagerank, eu_enrichment_count, eu_hit_count):
        if(pagerank is None or pagerank < 1): pagerank = 1
        #pagerank = pagerank + 1 # eliminate values > 1
        # two effects: pagerank only boosts values
        # old: no europeana hits drops relevance to zero
        # old: no pagerank value leaves relevance as europeana hits
        # new: no enrichments for this entity found -> use term hits
        # new: use 1+ln(term hits) to reduce the effect of false positives (the search is ambiguous)
        #relevance = 0;
        #for organizations the default enrichment count is set to 1
        if(eu_enrichment_count > 1):
            relevance = eu_enrichment_count * pagerank
        elif(eu_hit_count > 0):
            relevance = (1 + math.log(eu_hit_count, 10)) * pagerank   
        else:    
            return 0
        
        deprecation_factor = 1
        if(id in self.penalized_entities):
            deprecation_factor = 0.5
        normed_relevance = math.floor(math.log(relevance) * 10000) * deprecation_factor
        return normed_relevance

    def calculate_normalized_score(self, pagerank, eu_enrichment_count, eu_hit_count):
        entity_type = self.name
        normalized_pr = self.calculate_normalized_metric_value(entity_type, self.METRIC_PAGERANK, pagerank)
        normalized_eh = self.calculate_normalized_metric_value(entity_type, self.METRIC_ENRICHMENT_HITS, eu_enrichment_count)
        normalized_th = self.calculate_normalized_metric_value(entity_type, self.METRIC_TERM_HITS, eu_hit_count)
        normalized_score = normalized_pr * max(normalized_eh, normalized_th)
                            
        return math.floor(normalized_score * self.RANGE_EXTENSION_FACTOR)
        
    
    def calculate_normalized_metric_value(self, entity_type, metric, metric_value):
        #min value for normalized value = 1
        if(metric_value <= 1):
            return 1
        #TODO check if deprecation list is needed 
        coordination_factor = self.coordination(entity_type, metric)
        normalized_metric_value = 1 + self.trust(metric) * math.log(coordination_factor * metric_value)
        return normalized_metric_value    
    
    def coordination(self, entity_type, metric):
        max_of_metric = max(self.METRIC_MAX_VALS[metric].values()) 
        max__of_metric_for_type = self.METRIC_MAX_VALS[metric][entity_type]   
        #enforce result as float
        return max_of_metric / float(max__of_metric_for_type);
    
    def trust(self, entity_type):
        return self.METRIC_TRUST[entity_type]
    
class AgentRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, self.AGENT)

class ConceptRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, self.CONCEPT)

class PlaceRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, self.PLACE)

class OrganizationRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, self.ORGANIZATION)

    def get_enrichment_count(self, uri):
        #TODO add proper implementation of counting items for organizations
        print("return default enrichment count 1 for organization: " + uri)
        return 1

    #def get_label_count(self, representation):
    #    #TODO add proper implementation of counting enrichments with organizations
    #    print("return default value for label count: 1")
    #   return 1

