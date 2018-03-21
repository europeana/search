import requests
from math import log2

rankings = {}
strings_to_ids = {}

AUTOSUGGEST_API = "http://test-entity.europeana.eu/entity/suggest?wskey=apidemo&text="

with open('../test_strings.txt', 'r') as tests:
    for line in tests:
        (_, auto_string, sought_id) = line.split("\t")
        strings_to_ids[auto_string] = sought_id.strip()

for key in strings_to_ids:
    req = AUTOSUGGEST_API + key
    res = requests.get(req).json()
    i = 0
    for contained in res['contains']:
        i += 1
        test_id = contained['@id']
        print(strings_to_ids[key])
        if(test_id == strings_to_ids[key]):
            print('triggered at ' + str(i))
            rankings[key] = i
            break
    if key not in rankings: rankings[key] = 0

with open('test_ranks.txt', 'w') as testranks:
    ranks = []
    for key in rankings.keys():
        ndcg = 0
        if(rankings[key] > 1):
            ndcg = 1 / log2(rankings[key])
        elif(rankings[key] == 1):
            ndcg = 1
        testranks.write(key + "\t\t" + str(ndcg) + "\n")
        ranks.append(ndcg)
    testranks.write("\n\nAVG NDCG: " + str(sum(ranks) / len(ranks)))






