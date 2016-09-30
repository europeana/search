import requests

class RelevanceCounter:

    # we want a general class that stores unique keys
    # along with a count of this key from a variety of web sources
    # Wikipedia, Europeana db, etc.

    # general pattern - check to see if entry exists
    # if so, retrieve count
    # if not, query for count and add to datastore

    MOSERVER = 'mongodb://136.243.103.29'
    MOPORT = 27017
    SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0"

    def __init__(self, name):
        import sqlite3 as slt
        self.name = name
        self.dbpath = "ranking_metrics/db/" + name + ".db"
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
        relevance = abs(eu_doc_count + eu_term_count) * abs(wpedia_count)
        if relevance == 0: return 0
        norm_factor = 1;
        inv = 1 / relevance
        normed = norm_factor - inv
        normed = float(format(normed, '.5f'))
        return normed

class EuDocRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'Europeana_DF')

    def normalize_string(self, normanda):
        return normanda

    def get_new_term_count(self, qry_term):
        import requests
        from pymongo import MongoClient

        # enrichment with the new identifiers has not been attempted
        # accordingly we need to first look up the old identifer, and then
        # search Solr based on *that*

        moclient = MongoClient(RelevanceCounter.MOSERVER, RelevanceCounter.MOPORT)
        solr_url = ""
        response = ""
        try:
            old_uri = moclient.annocultor_db.lookup.find_one({'codeUri':qry_term})['originalCodeUri']
            moclient.close()
            qry_term = "\"" + old_uri + "\"" # exact matching!
            solr_url = "http://sol1.eanadev.org:9191/solr/search_1/search"
            solr_url += "?q=" + qry_term
            solr_url += "&rows=0"
            solr_url += "&wt=json"
            response = requests.get(solr_url)
            return response.json()['response']['numFound']
        except TypeError:
            return 0

class WpediaRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'Wikipedia_clickstream')
        self.build_dictionary()


    def normalize_string(self, normanda):
        """
        :param normanda: a URI
        :return: normalised term retrieved from end of URI
        """
        import re

        normatus = normanda.split("/")[-1]
        normatus = RelevanceCounter.normalize_string(normatus)
        normatus = normatus.lower()
        return normatus

    def build_dictionary(self):
        self.freqs = {}
        with open("ranking_metrics/resources/wikipedia-click-frequencies.tsv", 'rU') as w:
            i = 0
            for line in w:
                (wiki,freq) = line.split("\t") #decoded!
                wiki = wiki.lower()
                self.freqs[wiki]=int(freq)
                # if (i % 100000 == 0): print("load " + str(i) +  " freqs");
                i+=1

    def get_term_count(self, qry_term):
        # TODO: unbodge this
        return self.get_new_term_count(qry_term)

    def get_new_term_count(self, qry_term):
        if(qry_term in self.freqs):
            return self.freqs[qry_term]
        else:
            # TODO: Implement Wpedia query
            return -1

class AgentRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'agent')

class PlaceRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'place')
