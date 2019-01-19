import requests
import time

SOLR_URI = "http://sol1.eanadev.org:9191/solr/search/search?q=*:*&wt=json&rows=0&facet=true&facet.limit=-1&facet.mincount=1"
DEFAULT_FACETS = ['UGC', 'LANGUAGE', 'TYPE', 'YEAR', 'PROVIDER', 'DATA_PROVIDER', 'COUNTRY', 'RIGHTS']
FASHION_FACETS = ['CREATOR', 'skos_concept', 'cc_skos_prefLabel.en', 'proxy_dc_format.en']
FASHION_FILTER = "PROVIDER:\"Europeana Fashion\""
TEST_URI = "http://144.76.218.178:9595/solr/facet_benchmark/search?wt=json&rows=0&q=*:*&facet=true&facet.mincount=1&facet.limit=-1"
TEST_FACETS = ['subject_uri', 'subject_term', 'type_uri', 'type_term']

def do_facet_request(facet, filtered=False, test=False):
    fqs = SOLR_URI + "&facet.field=" + facet
    if(test == True): fqs = TEST_URI + "&facet.field=" + facet
    if(filtered):
        fqs = fqs + "&fq=" + FASHION_FILTER
    start = time.time()
    print(fqs)
    frsp = requests.get(fqs)
    frsp.content
    roundtrip = time.time() - start
    frsp = frsp.json()
    num_vals = int(len(frsp['facet_counts']['facet_fields'][facet]) / 2)
    counts = frsp['facet_counts']['facet_fields'][facet][1::2]
    lengths = [len(lbl) for lbl in frsp['facet_counts']['facet_fields'][facet][0::2]]
    avg_length = sum(lengths) / num_vals
    print("Facet name: " + facet)
    print("Query time: " + str(roundtrip))
    print("Distinct values: " + str(num_vals))
    print("Total values: " + str(sum(counts)))
    print("Average value string-length: " + str(avg_length))
    print("\n")

def facet_request_real():
    print("DEFAULT FACETS")
    print("===============")
    for facet in DEFAULT_FACETS: do_facet_request(facet)

def fashion_facets_real():
    print("FASHION FACETS (all of Europeana)")
    print("=================================")
    for facet in FASHION_FACETS: do_facet_request(facet)

def filtered_fashion_facets_real():
    print("FASHION FACETS (Europeana only)")
    print("==============================")
    for facet in FASHION_FACETS: do_facet_request(facet, filtered=True)

def facet_request_test():
    print("TEST FACETS")
    print("=============")
    for facet in TEST_FACETS: do_facet_request(facet, test=True)

#facet_request_real()
#fashion_facets_real()
filtered_fashion_facets_real()
#facet_request_test()
