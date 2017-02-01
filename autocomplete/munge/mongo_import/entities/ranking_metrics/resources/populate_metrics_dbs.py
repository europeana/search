#
# A selection of utility scripts for creating or updating sqlite databases
# storing relevance information for Entity Collection entities.
#
# sqlite sturcture: one sqlite database for each entity type (Agent, Place, Concept)
# Each database holds a single table 'hits', with columns (id, wikipedia_hits,
# europeana_enrichment_hits, europeana_string_hits), where:
# id is the Europeana Entity Collection URI identifier of the entity
# wikipedia_hits is the number of visits that entity's Wikipedia page has received in a year
# europeana_enrichment_hits is the number of Europeana documents that contain the id of the entity
# europeana_string_hits is the number of Europeana documents returned by an OR search of all the
# entity's prefLabels
#
# Note that most of these functions take considerable time to execute, typically because
# they are querying a MongoDB and/or Solr at least once for every entity in the Entity
# Collection.  They should accordingly be run in a linux screen session to prevent
# dropped connections and the need to rerun the function from the beginning again.
#
# TODO: At the moment, these various functions are run on an ad-hoc basis. Monitor to
# determine whether a more engineered (Celery?) solution is required.

from pymongo import MongoClient
import json, requests, sqlite3
from sqlite3 import IntegrityError


SOLR_URI = "http://sol7.eanadev.org:9191/solr/search_2/search?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

def create_agent_record(old_agent_record, moclient, db):
    """
    Creates a new Agent record, retrieves its relevance info, and inserts
    this into the database.
    """
    # note that the old agent record  is required to load the agent's
    # Wikipedia metrics
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
    """
    Given a db and an id, returns a Boolean indicating whether the entity with
    that identifier is already present in the database
    """
    crsr = db.cursor()
    check = "SELECT * FROM hits WHERE id = '"  + id + "' LIMIT 1"
    test_rows = crsr.execute(check).fetchone()
    return bool(test_rows)

def load_agent_files():
    """
    Bulk load of all agents listed in the agent_metrics.json file
    """
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
    """
    Creates a new Place entity, retrieves its relevance info,
    and inserts this into the database
    """
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
    """
    Bulk load of all Places listed in the place_metrics.tsv file.
    """
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
    db.close()

def load_concept_files():
    """
    Bulk load of all concepts listed in the wikipedia-click-frequencies.tsv file.
    """
    MONGO_URI = "mongodb://136.243.103.29"
    MONGO_PORT = 27017
    moclient = MongoClient(MONGO_URI, MONGO_PORT)
    db = sqlite3.connect('../db/concept.db')
    csr = db.cursor()
    csr.execute("""
            CREATE TABLE IF NOT EXISTS hits (id VARCHAR(200) PRIMARY KEY, wikipedia_hits INTEGER, europeana_enrichment_hits INTEGER, europeana_string_hits INTEGER)
        """)
    wk_hits = {}
    with open('wikipedia-click-frequencies.tsv', 'rU') as wcf:
        for line in wcf:
            (term, hits) = line.split("\t")
            wk_hits[term] = hits.strip().replace("\n", "")
    concept_rows = moclient.annocultor_db.TermList.find({ "codeUri" :  { "$regex" : "/.*concept.*/" } })
    for concept in concept_rows:
        en_labels = []
        try:
            en_labels = concept['representation']['prefLabel']['en']
        except:
            try:
                en_labels = concept['representation']['prefLabel']['']
            except:
                pass
        wikipedia_hits = 0
        for en_label in en_labels:
            if(en_label in wk_hits.keys()):
                wikipedia_hits = wk_hits[en_label.strip().replace("\n", "")]
        id = concept['codeUri']
        try:
            enrichment_count = requests.get(SOLR_URI + "\"" + id + "\"").json()['response']['numFound']
        except:
            enrichment_count = 0
        try:
            all_labels = []
            [all_labels.extend(lang_labels) for lang_labels in concept['representation']['prefLabel'].values()]
            for lang_labels in concept['representation']['prefLabel'].values():
                for lang_label in lang_labels:
                    all_labels.append("\"" + lang_label + "\"")
            terms_qry = " OR ".join(all_labels)
            terms_count = requests.get(SOLR_URI + terms_qry).json()['response']['numFound']
        except:
            terms_count = 0
        vals = ["\"" + id + "\"", str(wikipedia_hits), str(enrichment_count), str(terms_count)]
        print(vals)
        insert = ",".join(vals)
        csr.execute("INSERT INTO hits VALUES(" + insert +  ")")
        db.commit()
    db.close()


def test_db_working(db_name, id):
    """
    Toy method for basic sanity checking
    """
    db_path = "../db/" + db_name + ".db"
    db = sqlite3.connect(db_path)
    csr = db.cursor()
    qry = "SELECT * FROM hits WHERE id='" + id + "';"
    for row in csr.execute(qry):
        print(row)

def enrichment_sanity_check():
    """
    Comprehensive sanity check
    """
    # test concept
    cdb = sqlite3.connect("../db/concept.db")
    ccsr = cdb.cursor()
    centity_id = "http://data.europeana.eu/concept/base/138"
    cqry = "SELECT * FROM hits WHERE id=\"" + centity_id + "\""
    crows = ccsr.execute(cqry)
    for crow in crows:
        print("Current row is " + str(crow))
    update_entity(centity_id, ccsr)
    cdb.commit()
    more_crows = ccsr.execute(cqry)
    for mcrow in more_crows:
        print("Updated row is " + str(mcrow))

    # test agent
    adb = sqlite3.connect("../db/agent.db")
    acsr = adb.cursor()
    aentity_id = "http://data.europeana.eu/agent/base/2"
    aqry = "SELECT * FROM hits WHERE id=\"" + aentity_id + "\""
    arows = acsr.execute(aqry)
    for arow in arows:
        print("Current row is " + str(arow))
    update_entity(aentity_id, acsr)
    adb.commit()
    more_arows = acsr.execute(aqry)
    for marow in more_arows:
        print("Updated row is " + str(marow))
    # test place
    pdb = sqlite3.connect("../db/place.db")
    pcsr = pdb.cursor()
    pentity_id = "http://data.europeana.eu/place/base/198081"
    pqry = "SELECT * FROM hits WHERE id=\"" + pentity_id + "\""
    prows = pcsr.execute(pqry)
    for prow in prows:
        print("Current row is " + str(prow))
    update_entity(pentity_id, pcsr)
    pdb.commit()
    more_prows = pcsr.execute(pqry)
    for parow in more_prows:
        print("Updated row is " + str(parow))

def update_concept_counts(): # self-explanatory
    db = sqlite3.connect("../db/concept.db")
    update_entity_class(db)

def update_agent_counts(): # self-explanatory
    db = sqlite3.connect("../db/agent.db")
    update_entity_class(db)

def update_place_counts(): # self-explanatory
    db = sqlite3.connect("../db/place.db")
    update_entity_class(db)

def update_entity_class(db):
    """
    Updates the metric information for every entity in the passed db.
    """
    csr = db.cursor()
    qry = """ SELECT * FROM hits WHERE id="http://data.europeana.eu/place/base/42377" """
    for row in csr.execute(qry):
        entity_id = row[0]
        ncsr = db.cursor()
        update_entity(entity_id, ncsr)
        db.commit()

def update_entity(entity_id, csr):
    """
    Updates the stored metric information for passed entity id
    """
    rich_hits = get_enrichment_count(entity_id)
    lbl_hits = get_label_count(entity_id)
    upd = "UPDATE hits SET europeana_enrichment_hits=" + str(rich_hits) + ",europeana_string_hits=" + str(lbl_hits) + " WHERE id=\"" + entity_id + "\";"
    csr.execute(upd)

def get_enrichment_count(entity_id):
    """
    Returns the number of documents in Europeana collections enriched with
    the relevant entity id
    """
    enrichment_query = SOLR_URI + "\"" + entity_id + "\""
    try:
        enrichment_resp = requests.get(enrichment_query).json()
        return enrichment_resp['response']['numFound']
    except KeyError:
        print("Enrichment query failed for entity " + entity_id)
        return -1

def get_label_count(entity_id):
    """
    Returns the number of hits for a given entity's prefLabels
    """
    ent = moclient.annocultor_db.TermList.find_one({ 'codeUri' : entity_id })
    try:
        ent_type = ent['entityType'].replace('Impl', '')
    except:
        return -1   
    field = "who"
    if(ent_type == "Concept"): field = "what"
    if(ent_type == "Place"): field = "where"
    query_terms = []
    # first, retrieve the prefLabel for every language from Mongo ...
    for lang in ent['representation']['prefLabel'].keys():
        terms = ent['representation']['prefLabel'][lang]
        for term in terms: query_terms.append(field + ":\"" + term + "\"")
    # ... then turn this into a giant OR query ...
    label_query_terms = set(query_terms)
    label_query_term = " OR ".join(label_query_terms)
    label_query = SOLR_URI + label_query_term
    try:
    # ... and return the result
        label_resp = requests.get(label_query).json()
        return label_resp['response']['numFound']
    except:
        print("Label query failed for entity " + entity_id)
        return -1

def update_places_with_wk_hits():
    """
    Updates every Place entity with the number of views it had in
    Wikipedia in the past year.
    """
    place_counts = {}
    with open('place_metrics.tsv', 'r') as places:
        for place in places:
            (geonames, _, _, _, wk_hits) = place.split("\t")
            place_counts[geonames] = wk_hits
    print(place_counts)
    db = sqlite3.connect("../db/place.db")
    csr = db.cursor()
    qry = """ SELECT * FROM hits """
    for row in csr.execute(qry):
        entity_id = row[0]
        ent = moclient.annocultor_db.lookup.find_one({ 'codeUri' : entity_id })
        as_geonames = ent['originalCodeUri']
        print(as_geonames + "!")
        try:
            wk_hits = place_counts[as_geonames]
        except KeyError:
            wk_hits = 0
        upd = "UPDATE hits SET wikipedia_hits=" + str(wk_hits) + " WHERE id=\"" + entity_id + "\";"
        print(upd)
        csr2 = db.cursor()
        csr2.execute(upd)
        db.commit()

def update_place_sanity_check():
    e = "http://data.europeana.eu/place/base/41947"
    db = sqlite3.connect("../db/place.db")
    csr = db.cursor()
    update_entity(e, csr)
    db.commit()
    ncsr = db.cursor()
    qry = "SELECT * FROM HITS WHERE id=\"" + e + "\""
    for row in ncsr.execute(qry):
        print("ID is " + row[0])
        print("Wikipedia Hits: " + str(row[1]))
        print("Enrichment Hits: " + str(row[2]))
        print("String Hits: " + str(row[3]))






# load_agent_files()
# test_db_working('place')
# load_place_files()
# load_concept_files()
# enrichment_sanity_check()
update_place_counts()
# update_agent_counts()
# update_concept_counts()
# update_places_with_wk_hits()
# update_place_sanity_check()
