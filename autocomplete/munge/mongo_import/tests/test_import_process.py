# ========================================================================#
#
# Tests to ensure import process is running correctly.
#
# Note the scope of these tests: they test only that the import process
# is yielding the expected output. They do nothing to validate the
# data of the imported entities.
#
#=========================================================================#
import requests, json


SOLR_URI = "http://entity-api.eanadev.org:9292/solr/production/select?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

# basic sanity check on entity count numbers
# check total
# check each entity type's counts

def test_totals():
    return False

# tests on a couple of entities of each type
def test_transform():
    return False

# presence of mandatory fields
def test_mandatory_fields():
    return False

# presence of non-mandatory but expected fields
def test_expected_fields():
    return False


# well-formedness and validity of payload JSON
# including in particular lack of line breaks in payload
def test_json_formation():
    return False
