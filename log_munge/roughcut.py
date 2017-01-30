# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections
from collections import namedtuple
import json

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)
s = Search(using=client, index="logstash-*")
q = Match(message={ "query" : "Search interaction", "type" : "phrase" })
s = s.query(q).query(~Q("match", message='"mlt"'))
s.aggs.bucket('ip', 'terms', field='ipv4').bucket('hourly', 'date_histogram', field='@timestamp', interval="hour").bucket('by_top_hit', 'top_hits', size=10)
r = s.execute()

#with open('output/output.txt', 'w') as INSPECT:
#    INSPECT.write(str(r.aggregations.buckets))

sessions = []

class Query:

    def __init__(self, term, constraints, result_count):
        self.term = term
        self.constraints = constraints
        self.result_count = result_count

    def add_timestamp(self, ts):
        self.timestamp = ""

class ItemQuery(Query):

    def __init__(self, term, record, constraints, result_count, rank):
        Query.__init__(self, term, constraints, result_count)
        self.record = record
        self.rank = rank

Session = namedtuple('ip', ['start_time', 'queries'] )
Constraint = namedtuple('constraint', ['parameter', 'value'])

#for hit in r.hits:
#    print("-----------------")
#    for el in hit:
#        print(el)

def get_query_and_constraints(params):
    params = params.replace("=>", ":")
    pardict = json.loads(params)
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
        total = msg[msg.rindex(":"):].strip()
        params = msg[msg.index('{'):msg.rindex('}') + 1]
        (query, constraints) = get_query_and_constraints(params)
        return Query(query, constraints, total)
    else:
        qbits = msg.split("Search parameters:")
        rec = qbits[0][len("Search interaction: * Record:"):qbits[0].rindex("*")].strip()
        params = qbits[1][qbits[1].index("{"):qbits[1].rindex("}") + 1]
        rank = qbits[1][qbits[1].rindex(":") + 1:].strip()
        total = qbits[1][qbits[1].index(":") + 1:qbits[1].rindex("*")].strip()
        (query, constraints) = get_query_and_constraints(params)
        return ItemQuery(query, rec, constraints, total, rank)

for address in r.aggregations.ip.buckets:
    ip = address.key
    for hourbound in address.hourly.buckets:
        hour = hourbound.key
        tophits = hourbound.by_top_hit
        for hit in hourbound.by_top_hit.hits.hits:
            query_id = hit._id
            newq = Search(using=client, index="logstash-*").query("match", _id=query_id)
            newr = newq.execute()
            for crit in newr:
                ts = crit['@timestamp']
                try:
                    qry = parse_message(crit.message)
                    qry.add_timestamp(ts)

                except:
                    pass
