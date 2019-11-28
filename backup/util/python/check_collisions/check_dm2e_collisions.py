from pymongo import MongoClient
import re

MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

with open('dm2e_collisions', 'w') as collisions:
    with open('dm2e_agent_ids', 'r') as ids:
        for id in ids:
            checkraw = id.strip().replace('http://data.dm2e.eu/data/agent/', '')
            checkenda = set(re.split(r'[\D]', checkraw))
            checkenda.discard('')
            print(checkenda)
            for checkendum in checkenda:
                idno = "http://data.europeana.eu/agent/base/" + str(checkendum)
                ent = moclient.annocultor_db.TermList.find_one({ 'codeUri' : idno })
                if(ent is None):
                    print("No hit found on " + idno)
                else:
                    print("Collision found on " + idno)
                    msg = id.strip() + "\t" + idno + "\n"
                    collisions.write(msg)
