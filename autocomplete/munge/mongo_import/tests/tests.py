# ========================================================================#
#
# Tests to ensure import process is running correctly.
#
# Note the scope of these tests: they test only that the import process
# is yielding the expected output. They do nothing to validate the
# data of the imported entities.
#
#=========================================================================#
import requests, json, os, sys
from pymongo import MongoClient
import entities.ContextClassHarvesters
import xml.etree.ElementTree as ET

SOLR_URI = "http://entity-api.eanadev.org:9292/solr/test/select?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)
# FM (FIELD_MAP) maps Mongo field names to XML @name values
FM = {}
for k, v in entities.ContextClassHarvesters.ContextClassHarvester.FIELD_MAP.items():
    FM[k] = v['label']

# IFM (INVERTED_FIELD_MAP) maps XML @name values to Mongo field names
IFM = {}
for k, v in FM.items():
    IFM[v] = k

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
    ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
    test_entities = [
         "http://data.europeana.eu/agent/base/11241",   # Paris Hilton
         "http://data.europeana.eu/agent/base/146741",  # Leonardo da Vinci
         "http://data.europeana.eu/place/base/40361",   # Den Haag
         "http://data.europeana.eu/place/base/143914",  # Ferrara
         "http://data.europeana.eu/concept/base/214",   # Neoclassicism
         "http://data.europeana.eu/concept/base/207"    # Byzantine art
    ]
    for test_entity in test_entities:
        ieb.build_individual_entity(test_entity, is_test=True)
    return False

def test_against_reference():
    test_files_against_mongo('reference')
    return False

def test_files_against_mongo(filedir):

    fullpath = os.path.join(os.path.dirname(__file__), 'testfiles', filedir)
    for filename in os.listdir(fullpath):
        struct = ET.parse(os.path.join(fullpath, filename))
        # we can assume a document of the structure [root]/add/doc/field
        # with there being only one <doc> element per document

        # first we create a hash of the xml structure
        doc = struct.getroot().findall('doc')
        all_fields = set([field.attrib['name'] for field in doc[0].iter('field')])
        from_xml = {}
        for field in all_fields:
            rel_fields = doc[0].findall('field[@name="' + field + '"]')
            vals = [rel_field.text for rel_field in rel_fields]
            from_xml[field] = vals
        from_mongo = {}
        mongo_rec = moclient.annocultor_db.TermList.find_one({ 'codeUri' : from_xml['id'][0]})
        mongo_rep = mongo_rec['representation']
        for mkey in mongo_rep.keys():
            mval = mongo_rep[mkey]
            if(type(mval) is list):
                from_mongo[mkey] = [item for item in mval]
            elif(type(mval) is dict):
                for k, v in mval.items():
                    from_mongo[mkey + "." + k] = [item for item in mval[k]]
            else: # if single value
                from_mongo[mkey] = [mval]
        # TODO: now that we have our hashes, we just have to compare them
        # first, we check the fields
        missing_from_mongo = [xml_key for xml_key in from_xml.keys() if (trim_lang_tag(xml_key) in IFM.keys() and xml_to_mongo(xml_key) not in from_mongo.keys())]
        missing_from_xml = [mog_key for mog_key in from_mongo.keys() if (trim_lang_tag(mog_key) in FM.keys() and mongo_to_xml(mog_key) not in from_xml.keys())]
        print("Missing from mongo: " + str(missing_from_mongo))
        print("Missing from XML: " + str(missing_from_xml))

def trim_lang_tag(field_name):
    return field_name.split(".")[0]

def xml_to_mongo(field_name):
    unqualified_field = field_name.split(".")[0]
    try:
        lang_qualifier = "." + field_name.split(".")[1]
    except:
        lang_qualifier = ""
    return IFM[unqualified_field] + lang_qualifier

def mongo_to_xml(field_name):
    unqualified_field = field_name.split(".")[0]
    try:
        lang_qualifier = "." + field_name.split(".")[1]
    except:
        lang_qualifier = ""
    return FM[unqualified_field] + lang_qualifier


# presence of mandatory fields
def test_mandatory_fields():
    # note that there are no mandatory fields defined
    # for individual contextual classes

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

test_against_reference()
