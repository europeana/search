# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=30)
s = Search(using=client, index="logstash-*")
q = Match(message={ "query" : "Search interaction", "type" : "phrase" })
s = s.query(q)
s.aggs.bucket('ip', 'terms', field='ipv4').bucket('by_top_hit', 'top_hits', size=10)
# TODO: Add sub-aggregation for timestamps with intervals of one hour
r = s.execute()

print(r.aggregations.ip.buckets)
