from pymongo import MongoClient

MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

with open('place_collisions', 'w') as collisions:
    with open('noneu_place_ids', 'r') as ids:
        for id in ids:
            idno = id.split("/")[-1].strip()
            idno = "http://data.europeana.eu/place/base/" + str(idno)
            ent = moclient.annocultor_db.TermList.find_one({ 'codeUri' : idno })
            if(ent is not None):
                msg = id.strip() + "\t" + idno + "\n"
                collisions.write(msg)
