from pymongo import MongoClient

MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

with open('collisions', 'w') as collisions:
    with open('noneu_ids', 'r') as ids:
        for id in ids:
            if("/" in id):
                idno = id.split("/")[-1].strip()
            else:
                idno = id.split(".")[-1].strip()
            idno = "http://data.europeana.eu/agent/base/" + str(idno)
            ent = moclient.annocultor_db.TermList.find_one({ 'codeUri' : idno })
            if(ent is None):
                print("No hit found on " + idno)
            else:
                print("Collision found on " + idno)
                msg = id.strip() + "\t" + idno + "\n"
                collisions.write(msg)
