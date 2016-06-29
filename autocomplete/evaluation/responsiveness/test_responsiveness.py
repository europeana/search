import requests
import time

COMPLETE_HANDLER = "http://144.76.218.178:9191/solr/ec_dev_cloud/suggestEntity?wt=json&indent=true&q="

test_strings = []
with open('../test_strings.txt', 'r') as testfile:
    for line in testfile:
        (_, namestub, _) = line.split("\t")
        test_strings.append(namestub)

test_times = []

for test_string in test_strings:
    i = 3
    while(i <= len(test_string)):
        txt = test_string[0:i]
        req = COMPLETE_HANDLER + txt
        start = time.time()
        res = requests.get(req)
        res.content
        roundtrip = time.time() - start
        test_times.append(roundtrip)
        i += 1

with open('test_times.txt', 'w') as log:
    for time in test_times:
        log.write(str(time) + "\n")
    avg = sum(test_times) / len(test_times)
    log.write("\n\nAVG: " + str(avg))


