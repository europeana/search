class RelevanceCounter:

    # we want a general class that stores unique keys
    # along with a count of this key from a variety of web sources
    # Wikipedia, Europeana db, etc.

    # general pattern - check to see if entry exists
    # if so, retrieve count
    # if not, query for count and add to datastore

    MOSERVER = 'mongodb://136.243.103.29'
    MOPORT = 27017

    def __init__(self, name):
        import sqlite3 as slt

        self.name = name
        self.dbpath = "ranking_metrics/db/" + name + "_db"
        self.db = slt.connect(self.dbpath)
        csr = self.db.cursor()
        csr.execute("""
            CREATE TABLE IF NOT EXISTS counts (id INTEGER PRIMARY KEY, name TEXT, total INTEGER)
        """)
        self.db.commit()

    def normalize_string(self, normanda):
        import re

        normatus = re.sub("[()[]\",]", " ", normanda.strip())
        normatus = re.sub("\s+", " ", normatus)
        normatus = re.sub(" ", "_", normatus)
        return normatus

    def get_term_count(self, qry_term):
        qry_term = self.normalize_string(qry_term)
        csr = self.db.cursor()
        csr.execute("SELECT name,total FROM counts WHERE name=?", (qry_term,))
        first_row = csr.fetchone()
        if(first_row is not None):
            return first_row[1]
        else:
            new_count = self.get_new_term_count(qry_term)
            z = csr.execute("INSERT INTO counts(name, total) VALUES (?, ?)", (qry_term, new_count))
            self.db.commit()
            return new_count

    def calculate_relevance_score(self, eu_doc_count, wpedia_count):
        relevance = abs(eu_doc_count) * abs(wpedia_count)
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
    #    counter = 0
    #    for k,v in self.freqs.items():
    #        print(k)
    #        self.get_term_count(k)
    #        counter += 1
    #    self.db.commit()

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

class DbpediaRelevanceCounter(RelevanceCounter):

    def __init__(self, same_as_count):
        RelevanceCounter.__init__(self, 'Dbpedia_sameAs')
        self.sac = same_as_count

    def get_term_count(self, qry_term):
        return self.sac

class AgentRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'agent_relevance')
        self.build_dictionary()

    def build_dictionary(self):
        import json
        hitjson = ''
        with open('ranking_metrics/resources/agent_metrics.bk.json') as rf:
            hitjson = json.load(rf)
        self.freqs = {}
        for val in hitjson:
            if("wikipedia_clicks" in val and "europeana_df" in val and "uri" in val):
                temp = {}
                temp["wpedia_clicks"] = val["wikipedia_clicks"]
                temp["eu_df"] = val["europeana_df"]
                self.freqs[val["uri"]] = temp

    def get_term_count(self, qry_term):
        try:
            agent_dict = self.freqs[qry_term]
            return agent_dict
        except KeyError:
            return { 'wpedia_clicks': 0, 'eu_df': 0 }

class PlaceRelevanceCounter(RelevanceCounter):

    def __init__(self):
        RelevanceCounter.__init__(self, 'place_relevance')
        self.build_dictionary()

    def build_dictionary(self):
        # parse sorted_both_places file into handy dictionary
        self.freqs = {}
        with open('ranking_metrics/resources/place_metrics.tsv') as pm:
            for line in pm:
                (old_id, new_id, label, wk_count, eu_count) = line.split("\t")
                if(old_id in self.freqs):
                    self.freqs[old_id]['eu_hits'] = int(self.freqs[old_id]['eu_hits']) + int(eu_count.strip())
                    self.freqs[old_id]['wk_hits'] = int(self.freqs[old_id]['wk_hits']) + int(wk_count.strip())
                else:
                    self.freqs[old_id] = {}
                    self.freqs[old_id]['eu_hits'] = int(eu_count.strip())
                    self.freqs[old_id]['wk_hits'] = int(wk_count.strip())

    def get_term_count(self, qry_term):
        try:
            place_dict = {}
            place_dict['wpedia_clicks'] = self.freqs[qry_term]['wk_hits']
            place_dict['eu_df'] = self.freqs[qry_term]['eu_hits']
            return place_dict
        except KeyError:
            return { 'wpedia_clicks': 0, 'eu_df': 0 }



