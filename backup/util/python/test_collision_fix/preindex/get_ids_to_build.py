import requests, json, urllib.parse
with open('testents', 'r') as testents:
    docs = []
    for line in testents.readlines():
        uri = line.strip()
        hread = (urllib.parse.unquote(uri[uri.find('q=') + 2:uri.find('&')])).replace('+', ' ')
        r = requests.get(uri)
        j = r.json()
        for doc in j['response']['docs']:
            did = doc['europeana_id']
            if(did not in docs): docs.append(did)

with open('test_entities.txt', 'w') as tout:
    for doc in docs:
        tout.write(doc + "\n")
