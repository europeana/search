from pymongo import MongoClient
import requests
from celery import Celery, chain, group
from celery.utils.log import get_task_logger
from requests import ConnectionError
from pymongo.errors import ServerSelectionTimeoutError

app = Celery('df_task', broker='redis://localhost:6379/', backend='redis://localhost:6379/')
logger = get_task_logger(__name__)

def get_all_places():
    client = MongoClient('136.243.103.29', 27017)
    all_places = client.annocultor_db.lookup.find({'codeUri' : { '$regex' :'http://data.europeana.eu/place/base/*'}})
    client.close()
    return all_places

@app.task(name='mongo_import.build_solr_qs', bind=True, default_retry_delay=3, max_retries=5)
def build_solr_qs(self, place):
    solr_url = "http://sol1.ingest.org:9191/solr/search_1/search?rows=0&wt=json&q="
    ol = place['originalCodeUri']
    solr_qry = solr_url + "\"" + ol + "\""
    qo = {}
    qo['label'] = ol
    qo['query'] = solr_qry
    return qo

@app.task(name='mongo_import.get_df', bind=True, default_retry_delay=3, max_retries=5)
def get_df(self, qo):
    with open('all_places_eu.txt', 'a') as writefile:
        count_string = ""
        try:
            count_string = query_solr(qo['label'], qo['query'])
        except Exception:
            count_string = qo['label'] + "\tERR"
        finally:
            writefile.write(count_string + "\n")
    writefile.close()

@app.task(name='mongo_import.query_solr', bind=True, default_retry_delay=3, max_retries=5)
def query_solr(self, label, solr_qry):
    try:
        response = requests.get(solr_qry)
        count_string = label + "\t" + str(response.json()['response']['numFound'])
        return count_string
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)

def get_unique_place_ids():
    from pymongo import MongoClient
    cl = MongoClient('136.243.103.29', 27017)
    all_ids = cl.annocultor_db.place.distinct('codeUri')
    cl.close()
    return all_ids

@app.task(name='mongo_import.get_place_records', bind=True, default_retry_delay=3, max_retries=5)
def get_place_records(self, id):
    from pymongo import MongoClient
    try:
        cl = MongoClient('136.243.103.29', 27017)
        id_records = cl.annocultor_db.lookup.find({ 'originalCodeUri' : id})
        new_ids = get_new_ids(id_records)
        id_with_labels = populate_id_and_labels(cl, id, new_ids)
    except ServerSelectionTimeoutError as ss:
        raise self.retry(exc=ss)
    cl.close()
    return id_with_labels

def get_new_ids(id_records):
    new_ids = []
    for idr in id_records:
        new_ids.append(idr['codeUri'])
    return new_ids

def populate_id_and_labels(conn, old_id, new_id_list):
    # so this will give us a triple map
    # each old id with a map of new ids, composed of name and count
    # old_id[new_id[label] = count]
    id_with_labels = {}
    id_with_labels[old_id] = {}
    for new_id in new_id_list:
        id_with_labels[old_id][new_id] = {}
        new_places = conn.annocultor_db.place.find({ 'codeUri' : new_id })
        for place in new_places:
             id_with_labels[old_id][new_id][place['originalLabel']] = 0
    return id_with_labels

@app.task(name='mongo_import.get_wpedia_hit_counts', bind=True, default_retry_delay=3, max_retries=5)
def get_wpedia_hit_counts(self, idwl):
    url_base = 'http://stats.grok.se/json/en/latest90/'
    labels = idwl['label']
    temp_labels = {}
    for label, count in labels.items():
        search_label = label.replace(" ", "_")
        count_url = url_base + search_label
        try:
            response = requests.get(count_url)
            counts = response.json()['daily_views']
            counter = 0
            for date, date_count in counts.items():
                counter += date_count
            temp_labels[label] = counter
        except ConnectionError as ce:
            raise self.retry(exc=ce)
    idwl['label'] = temp_labels
    return idwl

def build_df_list():
    populated_places = []
    with open("all_places_eu.txt", 'r') as ape:
        i = 0
        for line in ape:
            (place,freq) = line.split("\t") #decoded!
            populated_places.append(place)
            if (i % 100000 == 0): print("load " + str(i) +  " freqs");
            i+= 1
    return populated_places

@app.task(name='mongo_import.write_wpedia_hits', bind=True, default_retry_delay=3, max_retries=5)
def write_wpedia_hits(self, idwl):
    countstring = idwl['id'] + "\t"
    counter = 0
    for label, count in idwl['label'].items():
        counter += count
    countstring += str(counter)
    countstring += "\n"
    with open('all_places_wkpd.txt', 'a') as writefile:
        writefile.write(countstring)
    writefile.close()










