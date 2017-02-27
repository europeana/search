# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
from collections import namedtuple, OrderedDict
import datetime
import json, sys, urllib, re

def query_for_filters(start_time, end_time):
    initsearch = Search(using=client, index="logstash-*")
    api_search = initsearch.query('bool', filter=Q("exists", field="wskey"))
    filter_search = api_search.query(Match(url_query={"query" : "qf"}))
    temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(start_time) + "Z",'lte': datetime.datetime.isoformat(end_time) + "Z"}}})
    temp_search = filter_search.query('bool', filter=[temporal_filter])
    total_by_keys = {}
    for hit in temp_search.scan():
        wskey = hit['wskey']
        try:
            total_by_keys[wskey]["count"] += 1
        except KeyError:
            total_by_keys[wskey] = {}
            total_by_keys[wskey]["count"] = 1
        msg = hit['url_query']
        if("qf" not in msg): continue
        args = msg.split("&")
        for arg in args:
            if (arg.startswith("qf")):
                # let's tidy up a little
                arg = arg[3:]
                arg=urllib.parse.unquote(arg)
                arg = arg.replace("+", " ").replace("OR", " ").replace("AND", " ").replace("NOT", " ")
                for match in re.findall("\w+:", arg):
                    field = match[:-1]
                    try:
                        total_by_keys[wskey][field] += 1
                    except KeyError:
                        total_by_keys[wskey][field] = 1
    # now let's output the result
    outfile_name = "filters_by_api_key" + str(start_time) + ".txt"
    with open('output/logs/filters/' + outfile_name, 'w') as keyout:
        for k in sorted(total_by_keys, key=lambda z : total_by_keys[z]["count"], reverse=True):
            key_header = "Key: " + str(k) + "\tTotal Requests: " + str(total_by_keys[k]["count"]) + "\n"
            keyout.write(key_header)
            fields_requested = total_by_keys[k]
            for field_requested in sorted(fields_requested, key = lambda x : fields_requested[x], reverse=True):
                if(field_requested != "count"):
                    msg = "\t"+ field_requested + "\t" + str(total_by_keys[k][field_requested]) + "\n"
                    keyout.write(msg)
    print("Completed processing filters for " + str(start_time))

def query_for_facets(start_time, end_time):
    initsearch = Search(using=client, index="logstash-*")
    api_search = initsearch.query('bool', filter=Q("exists", field="wskey"))
    facet_search = api_search.query(Match(url_query={"query" : "facet="}))
    temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(start_time) + "Z",'lte': datetime.datetime.isoformat(end_time) + "Z"}}})
    temp_search = facet_search.query('bool', filter=[temporal_filter])
    total_by_keys = {}
    for hit in temp_search.scan():
        wskey = hit['wskey']
        try:
            total_by_keys[wskey]["count"] += 1
        except KeyError:
            total_by_keys[wskey] = {}
            total_by_keys[wskey]["count"] = 1
        msg = hit['url_query']
        facet_lists = [urllib.parse.unquote(facet_list.replace("facet=", "")) for facet_list in msg.split("&") if facet_list.startswith("facet=")]
        for facet_list in facet_lists:
            facets_as_list = facet_list.split(",")
            for facet in facets_as_list:
                facet = facet.strip()
                try:
                    total_by_keys[wskey][facet] += 1
                except KeyError:
                    total_by_keys[wskey][facet] = 1
    # now let's output the result
    outfile_name = "facets_by_api_key" + str(start_time) + ".txt"
    with open('output/logs/facets/' + outfile_name, 'w') as keyout:
        for k in sorted(total_by_keys, key=lambda z : total_by_keys[z]["count"], reverse=True):
            key_header = "Key: " + str(k) + "\tTotal Requests: " + str(total_by_keys[k]["count"]) + "\n"
            keyout.write(key_header)
            fields_requested = total_by_keys[k]
            for field_requested in sorted(fields_requested, key = lambda x : fields_requested[x], reverse=True):
                if(field_requested != "count"):
                    msg = "\t"+ field_requested + "\t" + str(total_by_keys[k][field_requested]) + "\n"
                    keyout.write(msg)
    print("Completed processing facets for " + str(start_time))

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)
# start_date = "2017-01-14T00:00:00.005Z"
start_date = "2017-02-01T01:00:00.005Z"
current_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")

while(current_date < datetime.datetime.now()):
    hour_chunk = 1
    end_date = current_date + datetime.timedelta(hours=hour_chunk)
#    query_for_filters(current_date, end_date)
    query_for_facets(current_date, end_date)
    current_date = end_date
