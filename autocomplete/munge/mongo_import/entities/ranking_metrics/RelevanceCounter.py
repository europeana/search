import requests

class RelevanceCounter:
    """
       Calculates the relevance of a given entity, based on three factors:
       the number of clicks that entity's Wikipedia page has received over the
       past year; the number of enrichments using the entity's URL found in
       Europeana datastores; and the number of exact-match hits an OR query
       using the entity's various language labels retrieves.


       In terms of process, this class is very simple: while processing each
       entity, it checks to see whether the above metrics are already stored
       in the relevant sqlite dagabas. If so, it retrieves the results; if not,
       it calculates the Europeana-related metrics (enrichment and term count)
       and inserts these into the database for later retrieval.
   """

    MOSERVER = 'mongodb://136.243.103.29'
    MOPORT = 27017
    SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0"

    def __init__(self, name):
        import sqlite3 as slt
        import sys, os
        self.name = name
        self.dbpath = os.path.join(os.path.dirname(__file__), 'db', name + ".db")
        self.db = slt.connect(self.dbpath)

    def normalize_string(self, normanda):
        import re

        normatus = re.sub("[()[]\",]", " ", normanda.strip())
        normatus = re.sub("\s+", " ", normatus)
        normatus = re.sub(" ", "_", normatus)
        return normatus

    def get_raw_relevance_metrics(self, id, representation):
        csr = self.db.cursor()
        csr.execute("SELECT * FROM hits WHERE id=?", (id,))
        first_row = csr.fetchone()
        if(first_row is not None):
            (_, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits) = first_row
        else:
            wikipedia_hits = -1
            europeana_enrichment_hits = self.get_enrichment_count(id)
            europeana_string_hits = self.get_label_count(representation)
            z = csr.execute("INSERT INTO hits(id, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits) VALUES (?, ?, ?, ?)", (id, wikipedia_hits, europeana_enrichment_hits, europeana_string_hits))
            self.db.commit()
        metrics = {
            "wikipedia_hits" : wikipedia_hits,
            "europeana_enrichment_hits" : europeana_enrichment_hits,
            "europeana_string_hits" : europeana_string_hits
        }
        return metrics

    def get_enrichment_count(self, id):
        qry = RelevanceCounter.SOLR_URI + "?q=\"" + id + "\""
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

    def calculate_relevance_score(self, wpedia_count, eu_doc_count, eu_term_count):
        # TODO: thie method of calculation results in values that are too high
        # and not widely spread. Recalibrate.
        relevance = abs(eu_doc_count) * abs(eu_term_count) * abs(wpedia_count)
        if relevance == 0: return 0
        norm_factor = 1;
        inv = 1 / relevance
        normed = (norm_factor - inv) * 1000
        # normed = float(format(normed, '.5f'))
        return normed

class AgentRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'agent')

class ConceptRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'concept')

class PlaceRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'place')
