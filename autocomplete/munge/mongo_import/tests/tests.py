# ========================================================================#
#
# Tests to ensure import process has run correctly.
#
# Note the scope of these tests: they test only that the import process
# is yielding the expected output. They do nothing to validate the
# data of the imported entities itself.
#
#=========================================================================#

import requests, json, os, sys, re, time
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

class StatusReporter:

    def __init__(self, status, test_name, entity_id, msg):
        self.status = status
        self.test_name = test_name
        self.entity_id = entity_id
        self.msg = msg

    def display(self, suppress_stdout=False, log_to_file=False):
        msg = self.test_name + " "
        if(self.status == "OK"):
            msg += "PASSED"
        else:
            msg += "FAILED"
        msg += " on " + self.entity_id + ": " + self.msg
        if(not(suppress_stdout)): print(msg + "\n")
        if(log_to_file):
            filepath =  os.path.join(os.path.dirname(__file__), '..', 'logs', 'import_tests', 'transform.log')
            msg = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ": " + msg
            with open(filepath, 'a') as l:
                l.write(msg + "\n")

# basic sanity check on entity count numbers
# check total
# check each entity type's counts

def test_totals():

    # checking to make sure all entities successfully imported
    total_mongo_entities = int(moclient.annocultor_db.TermList.find({}).count())
    total_solr_entities = get_solr_total()
    if (total_mongo_entities == total_solr_entities):
        return [StatusReporter("OK", "Test Totals", "All entities", "Totals match: " + str(total_mongo_entities) + " in both datastores")]
    else:
        return [output_discrepancy(total_solr_entities, "Mongo", total_mongo_entities)]
    return False

def get_solr_total():
    try:
        slr_qry = SOLR_URI + "*:*"
        return int(requests.get(slr_qry).json()['response']['numFound'])
    except Exception as e:
        print("Failure to parse Solr server response: " + str(e))
        exit

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
    errors = test_files_against_mongo('dynamic')
    errors.extend(test_json_formation('dynamic'))
    return errors

def test_against_reference():
    errors = test_files_against_mongo('reference')
    errors.extend(test_json_formation('reference'))
    return errors

def test_files_against_mongo(filedir='reference'):
    status_reports = []
    fullpath = os.path.join(os.path.dirname(__file__), 'testfiles', filedir)
    for filename in os.listdir(fullpath):
        struct = ET.parse(os.path.join(fullpath, filename))
        # we can assume a document of the structure [root]/add/doc/field
        # with there being only one <doc> element per document

        # first we create a hash of the xml structure ...
        doc = struct.getroot().findall('doc')
        all_fields = set([field.attrib['name'] for field in doc[0].iter('field')])
        from_xml = {}
        for field in all_fields:
            rel_fields = doc[0].findall('field[@name="' + field + '"]')
            vals = [rel_field.text for rel_field in rel_fields]
            from_xml[field] = vals
        # ... then of the structure in mongo
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
        if(len(missing_from_mongo) > 0 or len(missing_from_xml) > 0):
            entity_type = from_xml["internal_type"][0]
            idno = from_xml["id"][0]
            et = entity_type + " " + str(idno.split("/")[-1])
            msg = ["Missing from mongo: " + str(missing_from_mongo)]
            msg.append("Missing from XML: " + str(missing_from_xml))
            test_name = "Test " + filedir + " files against Mongo"
            msg = "; ".join(msg)
            sr = StatusReporter("BAD", test_name, et, msg)
            status_reports.append(sr)
    return status_reports

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
    mandatory_fields = ['id', 'internal_type', 'europeana_doc_count',
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
        if(disc.status == "BAD"):
            errors.append(disc)
    if (len(errors) == 0):
        errors.append(StatusReporter("OK", "Mandatory Field Test", "All Entities", "All mandatory fields fully populated."))
    return errors

def output_discrepancy(solr_total, comparator_name, comparator_count, log=False):
    discrepancy = abs(solr_total - comparator_count)
    if (discrepancy == 0):
        return StatusReporter("OK", comparator_name + " Tally", "All Entities", "Solr and " + comparator_name + " counts tally")
    else:
        msg = ["Count mismatch between complete Solr count and " + comparator_name]
        msg.append("Solr (all documents): " + str(solr_total))
        msg.append(comparator_name + ": " + str(comparator_count))
        msg.append("Discrepancy: " + str(discrepancy))
        msg = "; ".join(msg)
        return StatusReporter("BAD", comparator_name + " Tally", "All Entities", msg)

# test no newlines in output
def test_json_formation(filedir):
    errors = []
    fullpath = os.path.join(os.path.dirname(__file__), 'testfiles', filedir)
    for filename in os.listdir(fullpath):
        struct = ET.parse(os.path.join(fullpath, filename))
        doc = struct.getroot().findall('doc')
        from_xml = {}
        even = False
        view = ""
        for field in doc[0].iter('field'):
            text = field.text
            fieldname = field.attrib['name']
            # payload fields contain JSON objects so escaping needs
            # different handling
            if(fieldname.startswith("payload")):
                teststring = "{\"" + fieldname + "\":" + text + "}"
                textbits = text.split('":')
                for bit in textbits:
                    if(even and '"' in bit):
                        firstbit = bit[:bit.find('"')]
                        lastbit = bit[bit.rfind('"'):]
                        midbit = bit[bit.find('"'):bit.rfind('"')].replace('"', "'")
                    even = not(even)
                text = '":'.join(textbits)
            else:
                text = text.replace('"', "'")
                teststring = "{\"" + fieldname + "\":\"" + text + "\"}"
            from_xml[fieldname] = text
            try:
                as_json = json.loads(teststring)
            except ValueError as ve:
                entity_id = from_xml["internal_type"] + str(from_xml["id"].split("/")[-1])
                errors.append(StatusReporter("BAD", "JSON validity test", entity_id, "Field " + fieldname + " with value " + text + " is not valid JSON"))
    return errors

def run_test_suite(suppress_stdout=False, log_to_file=False):
    errors = []
    errors.extend(test_totals())
    errors.extend(test_transform())
    errors.extend(test_against_reference())
    errors.extend(test_mandatory_fields())
    errors.extend(test_files_against_mongo())
    for error in errors: error.display(suppress_stdout, log_to_file)
