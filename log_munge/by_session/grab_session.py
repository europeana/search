from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
from collections import namedtuple, OrderedDict
import datetime
import json, sys, urllib, re

def write_sessions(session_list):
    with open('session_list_feb.txt', 'a') as sout:
        for session in session_list:
            session = session.strip() + "\n"
            sout.write(session)

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)

initsearch = Search(using=client, index="logstash-*")
session_search = initsearch.query('bool', filter=Q("exists", field="session_id"))
no_pcs = session_search.query(~Q("match", controller="PortalController")) # eliminates a lot of apparently-duplicated record requests
no_pcs.aggs.bucket('sessions', A('terms', field='session_id'))

start_time = "2017-02-01T00:00:00Z"
termination_time = datetime.datetime.strptime("2017-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
current_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")

session_ids = []

while(current_time < termination_time):
    try:
        end_time = current_time + datetime.timedelta(minutes=15)
        temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(current_time) + "Z",'lte': datetime.datetime.isoformat(end_time) + "Z"}}})
        temp_search = no_pcs.query('bool', filter=[temporal_filter])
        r = temp_search.execute()
        for session in r.aggregations.sessions.buckets:
            session_ids.append(session['key'])
        if(len(session_ids) > 10000):
            write_sessions(session_ids)
            session_ids = []
        current_time = end_time
    except Error as e:
        print(str(e) + " at " + str(current_time))

if(len(session_ids) > 0):
    write_sessions(session_ids)





# first, query for all session ids within temporal limits.
# Make a big list of this

# then grab all messages and record retrievals

# then split into two output streams
