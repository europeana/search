import requests
import time

url_prefix = "https://www.europeana.eu"
roundtrips = []

with open("url.list") as urls:
	for line in urls.readlines():
		now_url = url_prefix + line.strip()
		start_time = time.time()
		frsp = requests.get(now_url)
		frsp.content
		roundtrip = time.time() - start_time
		roundtrips.append(roundtrip)

avg = sum(roundtrips) / len(roundtrips)
print(avg)