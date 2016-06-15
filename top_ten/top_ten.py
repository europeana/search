import requests

top10_queries = [
    'pliniusza starszego',
    'gaismas pils',
    'leif rekdal',
    '101. gyalogezred',
    't boshoeve',
    'heinz petry 16',
    'kuk stavel',
    'vermeer',
    'Adressbuch Posen',
    'filippo carli'
]

SOLR_SHARD = 'http://sol1.eanadev.org:9191/solr/search_1/search?wt=json&fl=europeana_id,title&rows=10&q='

with open('query_results.txt', 'w') as wrout:
    for q in top10_queries:
        qry = SOLR_SHARD + q
        dot = requests.get(qry)
        res = dot.json()
        wrout.write(q + ":\n")
        for r in res['response']['docs']:
            title = '________' if 'title' not in r else r['title'][0]
            wrout.write("\t" + title + ": " + r['europeana_id'] + "\n")
        wrout.write("\n\n")
