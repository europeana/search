from pymongo import MongoClient
import requests
import json

client = MongoClient('136.243.103.29', 27017)
url_base = 'http://stats.grok.se/json/en/latest30/'
all_places = client.annocultor_db.place.find()

with open('all_places.txt', 'w') as writefile:
    for place in all_places:
        ol = place['originalLabel']
        url = url_base + ol
        response = requests.get(url)
        all_views = response.json()['daily_views']
        total = 0
        for date, date_count in all_views.items():
            total += date_count
        count_data = ol + "\t" + str(total) + "\n"
        writefile.write(count_data)
    writefile.close()


