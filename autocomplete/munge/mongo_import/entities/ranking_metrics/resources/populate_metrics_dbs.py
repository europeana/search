# creates and populates databases to store metric information in the Entity collection
from pymongo import MongoClient
import json, requests, sqlite3
from sqlite3 import IntegrityError
#from celery import delay
from cache_metrics import create_agent_record


SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

def create_agent_record(old_agent_record, moclient, db):
    solr_uri = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0&q="
    csr = db.cursor()
    id = old_agent_record['uri']
    ent = moclient.annocultor_db.TermList.find_one({ 'owlSameAs' : id })
    if(ent is not None and 'codeUri' in ent.keys()):
        new_id = ent['codeUri']
        if(is_present_in_db(db, new_id)): return
        wpedia_hits = old_agent_record['wikipedia_clicks']
        enrichment_query = solr_uri + "\"" + new_id + "\""
        enrichment_resp = requests.get(enrichment_query).json()
        try:
            enrichment_count = enrichment_resp['response']['numFound']
        except KeyError:
            return
        query_terms = []
        for lang in ent['representation']['prefLabel'].keys():
            terms = ent['representation']['prefLabel'][lang]
            for term in terms: query_terms.append("\"" + term + "\"")
        label_query_terms = set(query_terms)
        label_query_term = " OR ".join(label_query_terms)
        label_query = solr_uri + label_query_term
        label_resp = requests.get(label_query).json()
        try:
            label_count = label_resp['response']['numFound']
            vals = ["\"" + new_id + "\"", str(wpedia_hits), str(enrichment_count), str(label_count)]
            print(vals)
            insert = ",".join(vals)
            csr.execute("INSERT INTO hits VALUES(" + insert +  ")")
            db.commit()
        except:
            return
    db.commit()

def is_present_in_db(db, id):
    crsr = db.cursor()
    check = "SELECT * FROM hits WHERE id = '"  + id + "' LIMIT 1"
    test_rows = crsr.execute(check).fetchone()
    return bool(test_rows)

def load_agent_files():
    MONGO_URI = "mongodb://136.243.103.29"
    MONGO_PORT = 27017
    moclient = MongoClient(MONGO_URI, MONGO_PORT)
    db = sqlite3.connect('../db/agent.db')
    csr = db.cursor()
    csr.execute("""
            CREATE TABLE IF NOT EXISTS hits (id VARCHAR(200) PRIMARY KEY, wikipedia_hits INTEGER, europeana_enrichment_hits INTEGER, europeana_string_hits INTEGER)
        """)
    with open('agent_metrics.bk.json') as rf:
        hitjson = json.load(rf)
        for record in hitjson:
            create_agent_record(record, moclient, db)
    db.close()

def create_place_record(id, wk_hits, labels, db):
    solr_uri = "http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&rows=0&q="
    csr = db.cursor()
    enrichment_query = solr_uri + "\"" + id + "\""
    enrichment_resp = requests.get(enrichment_query).json()
    try:
        enrichment_count = enrichment_resp['response']['numFound']
    except KeyError:
        return
    uniq_labels = set(labels)
    quot_labels = ["\"" + l + "\"" for l in uniq_labels]
    qs = " OR ".join(quot_labels)
    qry = solr_uri + qs
    label_resp = requests.get(qry).json()
    try:
        label_count = label_resp['response']['numFound']
        vals = ["\"" + id + "\"", str(wk_hits), str(enrichment_count), str(label_count)]
        print(vals)
        insert = ",".join(vals)
        csr.execute("INSERT INTO hits VALUES(" + insert +  ")")
        db.commit()
        return
    except:
        return

def load_place_files():
    db = sqlite3.connect('../db/place.db')
    csr = db.cursor()
    csr.execute("""
            CREATE TABLE IF NOT EXISTS hits (id VARCHAR(200) PRIMARY KEY, wikipedia_hits INTEGER, europeana_enrichment_hits INTEGER, europeana_string_hits INTEGER)
        """)
    with open('place_metrics.tsv') as pm:
        counter = 0
        previous_id = ""
        wikipedia_hits = 0
        labels = []
        for line in pm:
            (_, new_id, label, wk_count, eu_count) = line.split("\t")
            if(new_id != previous_id and previous_id != ""):
                create_place_record(previous_id, wikipedia_hits, labels, db)
                wikipedia_hits = 0
                labels = []
            previous_id = new_id
            wikipedia_hits += int(wk_count)
            labels.append(label)
            counter += 1
            if(counter % 1000 == 0): print(str(counter) + " lines processed.")
    print("COMPLETE")
    db.close()


def test_db_working(db_name):
    db_path = "../db/" + db_name + ".db"
    db = sqlite3.connect(db_path)
    csr = db.cursor()
    qry = """ SELECT * FROM hits WHERE id='http://data.europeana.eu/place/base/100172'"""
    for row in csr.execute(qry):
        print(row)

# load_agent_files()
test_db_working('place')
# load_place_files()
