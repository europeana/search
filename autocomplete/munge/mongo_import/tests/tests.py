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
from pymongo import MongoClient
import entities.ContextClassHarvesters

SOLR_URI = "http://entity-api.eanadev.org:9292/solr/test/select?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)

# basic sanity check on entity count numbers
# check total
# check each entity type's counts

def test_totals():

    # Get total from Mongo
    total_mongo_entities = int(moclient.annocultor_db.TermList.find({}).count())
    total_solr_entities = get_solr_total()

    if (total_mongo_entities == total_solr_entities):
        print("Total count for Mongo and Solr datastores is: " + str(total_mongo_entities))
        return True
    else:
        output_discrepancy(total_solr_entities, "Mongo", total_mongo_entities)
    return False

def get_solr_total():
    try:
        slr_qry = SOLR_URI + "*:*"
        return int(requests.get(slr_qry).json()['response']['numFound'])
    except Exception as e:
        print("Failure to parse Solr server response: " + str(e))
        return -1

# tests on a couple of entities of each type
def test_transform():
    return False

# presence of mandatory fields
def test_mandatory_fields():
    # mandatory fields are: id, internal_type, europeana_doc_count
    # europeana_term_hits, wikipedia_clicks, suggest_filters, derived_score,
    # at least one skos_prefLabel, one payload
    # note that there are no mandatory fields for individual contextual classes

    errors = []
    mandatory_fields = ['id', 'internal_type', 'europeana_doc_count'
                        'europeana_term_hits', 'wikipedia_clicks', 'suggest_filters',
                        'derived_score', 'skos_prefLabel', 'payload']
    total_docs = get_solr_total()

    for mfield in mandatory_fields:
        qry = SOLR_URI + mfield + ":*"
        try:
            mfield_total = int(requests.get(qry).json()['response']['numFound'])
        except Exception as e:
            print("Could not parse response string: " + str(e))
            exit
        mlogo = "Mandatory " + mfield + " field"
        disc = output_discrepancy(total_docs, mlogo, mfield_total)
        if(disc != 0):
            errors.append(mfield)
    if (len(errors) == 0):
        print("************************************")
        print("All mandatory fields fully populated")
        print("************************************")
        return True
    return False

def output_discrepancy(solr_total, comparator_name, comparator_count, log=False):
    discrepancy = abs(solr_total - comparator_count)
    if (discrepancy == 0):
        print("=====================================")
        print("Solr and " + comparator_name + " counts tally")
    else:
        print("=====================================")
        print("WARNING: Count mismatch between complete Solr count and " + comparator_name)
        print("Solr (all documents): " + str(solr_total))
        print(comparator_name + ": " + str(comparator_count))
        print("Discrepancy: " + str(discrepancy))
        print("======================================")
    return int(discrepancy)
# well-formedness and validity of payload JSON
# including in particular lack of line breaks in payload
def test_json_formation():
    return False

# test_totals()
