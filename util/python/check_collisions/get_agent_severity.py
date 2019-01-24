import requests, json

SOLR_URI = "http://sol7.eanadev.org:9191/solr/search_2/search?wt=json&rows=0&q=text:"

DOIT = False
with open('agent_severity', 'a') as severity:
    with open('agent_collisions', 'r') as collisions:
        for clide in collisions:
            (orig, ours) = clide.split("\t")
            if(orig == "RM0001.PEOPLE.104158"): DOIT = True
            if(DOIT):
                orig_query = SOLR_URI + "\"" + orig + "\""
                our_query = SOLR_URI + "\"" + ours + "\""
                try:
                    orig_count = requests.get(orig_query).json()['response']['numFound']
                    our_count = requests.get(our_query).json()['response']['numFound']
                    msg = orig + "\t" + str(orig_count) + "\t" + ours + "\t" + str(our_count) + "\t" + str(orig_count + our_count) + "\n"
                except Exception as e:
                    msg = "Problem getting counts for " + orig_query + "|" + our_query + str(e)
                severity.write(msg)
