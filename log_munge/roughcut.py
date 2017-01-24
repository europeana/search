# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)
s = Search(using=client, index="logstash-*")
q = Match(message={ "query" : "Search interaction", "type" : "phrase" })
s = s.query(q)
s.aggs.bucket('ip', 'terms', field='ipv4').bucket('hourly', 'date_histogram', field='@timestamp', interval="hour").bucket('by_top_hit', 'top_hits', size=10)
r = s.execute()

with open('output/output.txt', 'w') as INSPECT:
    INSPECT.write(r.aggregations.ip.buckets)

print(r.aggregations.ip.buckets)
