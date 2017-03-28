from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
from collections import namedtuple, OrderedDict
import datetime
import json, sys, urllib, re

def load_session_ids():
    sessids = []
    with open('session_list_feb.txt', 'r') as sint:
        for line in sint.readlines():
            if(line.strip() != ""): sessids.append(line.strip())
    sessids = list(set(sessids))
    return sessids

def jsonify(as_string):
    params = as_string.replace("=>", ":")
    try:
        as_json = json.loads(params)
        return as_json
    except Exception as e:
        print("Failed to load params as JSON: " + str(e))

def get_query_and_constraints(params):
    pardict = jsonify(params)
    try:
        query = pardict['q']
    except:
        query = ""
    try:
        constraints = pardict['f']
    except:
        constraints = ""
    return (query, constraints)

def parse_message(msg):
    msg = msg.replace("\n", " ")
    if("Search interaction" not in msg):
        return [msg]
    elif(("Result rank:") not in msg):
        total = msg[msg.rindex(":") + 1:].strip()
        params = msg[msg.index('{'):msg.rindex('}') + 1]
        (query, constraints_as_json) = get_query_and_constraints(params)
        return [query, str(constraints_as_json), total]
    else:
        qbits = msg.split("Search parameters:")
        rec = qbits[0][len("Search interaction: * Record:"):qbits[0].rindex("*")].strip()
        params = qbits[1][qbits[1].index("{"):qbits[1].rindex("}") + 1]
        rank = qbits[1][qbits[1].rindex(":") + 1:].strip()
        total = qbits[1][qbits[1].index("Total hits:") + len("Total hits:"):qbits[1].rindex("*")].strip()
        (query, constraints_as_json) = get_query_and_constraints(params)
        return [query, rec, str(constraints_as_json), total, rank]

session_ids = load_session_ids()

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)

initsearch = Search(using=client, index="logstash-*")
no_pcs = initsearch.query(~Q("match", controller="PortalController")) # eliminates a lot of apparently-duplicated record requests
start_time = datetime.datetime.strptime("2017-02-03T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
end_time = datetime.datetime.strptime("2017-03-25T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(start_time) + "Z",'lte': datetime.datetime.isoformat(end_time) + "Z"}}})
temporal_search = no_pcs.query('bool', filter=[temporal_filter])

for session_id in session_ids:
    this_session = initsearch.query(Q("match", session_id=session_id)).sort('@timestamp')[:1000]
    r = this_session.execute()
    first_hit_ts = ""
    if(len(r.hits) > 0):
        first_hit_ts = r.hits[0]['@timestamp']
        filename = first_hit_ts + "_" + session_id + ".txt"
        filepath = "feb_sessions/" + filename
        with open(filepath, 'w') as sessout:
            for hit in r.hits:
                ts = hit['@timestamp']
                msg = "\t".join(parse_message(hit['message']))
                msgout = ts + "\t" + msg + "\n"
                if("[302]" not in msgout):
                    sessout.write(msgout)
