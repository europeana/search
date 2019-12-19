import requests, json

SOLR_URL = "http://sol7.eanadev.org:9191/solr/search_2_shard2_replica1/search?wt=json&fl=title,proxy_dc_creator&q="

just_term="\"Freud\""
unboosted_url="\"http://data.europeana.eu/agent/base/62141\" OR \"Freud\""
boosted_url = "\"http://data.europeana.eu/agent/base/62141\"ˆ2 OR \"Freud\""

chunk=500

def get_bugatti_rank(query_term):
    for i in range(0, 10000, chunk):
        start = str(i)
        qry = SOLR_URL + query_term + "&start=" + start + "&rows=" + str(chunk)
        print(qry)
        try:
            resp = requests.get(qry).json()
            # print(resp)
        except Exception as e:
            print(e)
        for j in range(0, chunk):
            try:
                cr = resp['response']['docs'][j]['proxy_dc_creator']
                for c in cr:
                    print(c)
                    if ('Sigmund' in c):
                        return str(i + j)
            except KeyError as ke:
                pass


br = get_bugatti_rank(unboosted_url)
print("Just term rank is " + br)
