# python package requirements
#      elasticsearch 5.1.0
#      elasticsearch 5.0.0
# (and any dependencies of these)

import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections

# constrain our search to the last 5 minutes
now = datetime.datetime.isoformat(datetime.datetime.utcnow()) + "Z"
before = datetime.datetime.isoformat(datetime.datetime.utcnow() - datetime.timedelta(minutes=15)) + "Z"
temporal_filter = Q({'range':{'@timestamp':{'gte': before,'lte': now}}})

# establish connection to ES
conn = connections.create_connection(hosts='http://elasticsearch2.eanadev.org:9200', timeout=60)
# create the query - looking for anything with BOTH a session ID and a message that includes the phrase "Search interaction"
initsearch = Search(using=conn, index="logstash-*").query('bool', filter=Q("exists", field="session_id")).query(Q("match", message="Search interaction")).query('bool', filter=[temporal_filter])[0:0]
resp = initsearch.execute()
# total should be > 0
search_count = resp.hits.total
print(search_count)
