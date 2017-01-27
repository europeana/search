# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
from collections import namedtuple, OrderedDict
import datetime
import json, sys

InitQuery = namedtuple('Query', 'timestamp term constraints result_count')
ItemQuery = namedtuple('ItemQuery', 'timestamp term record constraints result_count rank')

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
    if(("Result rank:") not in msg):
        total = msg[msg.rindex(":") + 1:].strip()
        params = msg[msg.index('{'):msg.rindex('}') + 1]
        (query, constraints) = get_query_and_constraints(params)
        return (query, constraints, total)
    else:
        qbits = msg.split("Search parameters:")
        rec = qbits[0][len("Search interaction: * Record:"):qbits[0].rindex("*")].strip()
        params = qbits[1][qbits[1].index("{"):qbits[1].rindex("}") + 1]
        rank = qbits[1][qbits[1].rindex(":") + 1:].strip()
        total = qbits[1][qbits[1].index("Total hits:") + len("Total hits:"):qbits[1].rindex("*")].strip()
        (query, constraints) = get_query_and_constraints(params)
        return (query, rec, constraints, total, rank)

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)
basesearch = Search(using=client, index="logstash-*")
start_date = "2017-01-14T00:01:00.005Z"
current_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
while(current_date < datetime.datetime.now()):
    print("Processing date " + datetime.datetime.isoformat(current_date))
    all_searches = OrderedDict()
    next_date = current_date + datetime.timedelta(minutes=15)
    date_prefix = datetime.datetime.isoformat(current_date)
    temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(current_date) + "Z",'lte': datetime.datetime.isoformat(next_date) + "Z"}}})
    initsearch = Search(using=client, index="logstash-*")[:10000]
    q = Match(message={ "query" : "Search interaction", "type" : "phrase" })
    initsearch = initsearch.query(q)
    initsearch = initsearch.query(~Q("match", message='"Result rank"'))
    initsearch = initsearch.query('bool', filter=[temporal_filter])
    initsearch = initsearch.sort('@timestamp')
    r = initsearch.execute()
    for hit in r.hits:
        ts = hit['@timestamp']
        msg = parse_message(hit['message'])
        query_term = msg[0]
        if(query_term != ""):
            q = InitQuery(ts, query_term, msg[1], msg[2])
            all_searches[query_term] = {}
            all_searches[query_term]["Initial Query"] = q
            all_searches[query_term]["Clicked Items"] = []
            t = Search(using=client, index="logstash-*").sort('@timestamp')[:10000]
            u = Match(message={ "query" : '"Result rank"', "type" : "phrase" })
            v = Match(message={ "query" : query_term, "type" : "phrase" })
            t = t.query(u).query(v).query('bool', filter=[temporal_filter])
            x = t.execute()
            for qhit in x.hits:
                qts = qhit['@timestamp']
                qmsg = parse_message(qhit['message'])
                qq = ItemQuery(qts, query_term, qmsg[1], qmsg[2], qmsg[3], qmsg[4])
                all_searches[query_term]["Clicked Items"].append(qq)
    for k in all_searches:
        with open("output/logs/query_terms" + date_prefix + ".txt", "a+") as QRY:
            QRY.write(k + "\n")
        with open("output/logs/queries_and_results" + date_prefix + ".txt", "a+") as OUT:
            OUT.write(k + ":\n")
            if(len(all_searches[k]["Clicked Items"]) == 0):
                total = all_searches[k]["Initial Query"].result_count
                OUT.write("\t" + all_searches[k]["Initial Query"].timestamp + "\tNO ITEM CLICKED OUT OF " + str(total) + " RETURNED.\n")
            for item in all_searches[k]["Clicked Items"]:
                msg = "\t".join([item.timestamp, item.record, str(item.constraints), item.rank, item.result_count])
                msg = "\t" + msg + "\n"
                OUT.write(msg)
    current_date = next_date
