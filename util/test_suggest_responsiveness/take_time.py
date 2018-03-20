import time
import requests
import json

strlength = 2

suggest_url = "https://www.europeana.eu/api/entities/suggest?wskey=api2demo&type=agent&text="

roundtrips = []

with open('entity.list') as ents:
	for line in ents.readlines():
		entname = line.strip()[0:strlength]
		strlength += 1
		if(strlength == 5): strlength = 20
		if(strlength > 20): strlength = 2
		now_url = suggest_url + entname
		start_time = time.time()
		frsp = requests.get(now_url)
		frsp.content
		roundtrip = time.time() - start_time
		roundtrips.append(roundtrip)

avg = sum(roundtrips) / len(roundtrips)
print(avg)
		



