# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

LS = "http://elasticsearch2.eanadev.org:9200/logstash-*/_search"
