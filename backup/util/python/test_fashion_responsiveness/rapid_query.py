import requests
import time

JUST_FACETS = "http://sol1.eanadev.org:9191/solr/search_1/search?q=*:*&wt=json&fq=PROVIDER:%22Europeana%20Fashion%22&facet=true&facet.field=CREATOR&facet.field=cc_skos_prefLabel.en&facet.field=skos_concept&facet.field=proxy_dc_format.en&rows=25"

raw_retr_times = []

def time_query(qry):
    start = time.time()
    req = requests.get(qry)
    req.content
    roundtrip = time.time() - start
    head_time =""
    head_time = req.json()['responseHeader']['QTime']
    return tuple([str(roundtrip), head_time])

for i in range(10):
    print("Executing query " + str(i))
    t = time_query(JUST_FACETS)
    print(str(t[0]))
    raw_retr_times.append(t)

print(raw_retr_times)
