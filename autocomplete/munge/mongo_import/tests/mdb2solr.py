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

SOLR_URI = "http://entity-acceptance.eanadev.org:9191/solr/acceptance/select?wt=json&rows=0&q="
# SOLR_URI = "http://144.76.218.178:9191/solr/ec_dev_cloud/select?wt=json&rows=0&q="
MONGO_URI = "mongodb://136.243.103.29"
MONGO_PORT = 27017
moclient = MongoClient(MONGO_URI, MONGO_PORT)
BIG_FM = entities.ContextClassHarvesters.ContextClassHarvester.FIELD_MAP
# FM (FIELD_MAP) maps Mongo field names to XML @name values
FM = {}
for k, v in BIG_FM.items():
    FM[k] = v['label']

# IFM (INVERTED_FIELD_MAP) maps XML @name values to Mongo field names
IFM = {}
for k, v in FM.items():
    IFM[v] = k

ALL_ENT_TYPES = ['concept', 'agent', 'place', 'all']

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
    total_mongo_entities = int(moclient.annocultor_db.TermList.find({ "codeUri" : { "$regex" : "http://data.europeana.eu/.*" }}).count())
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
        sys.exit()

# tests on a couple of entities of each type
def test_transform():
    ieb = entities.ContextClassHarvesters.IndividualEntityBuilder()
    test_entities = [
         "http://data.europeana.eu/agent/base/11241",   # Paris Hilton
         "http://data.europeana.eu/agent/base/146741",  # Leonardo da Vinci
         "http://data.europeana.eu/place/base/40361",   # Den Haag
         "http://data.europeana.eu/place/base/143914",  # Ferrara
         "http://data.europeana.eu/place/base/216272",  # Japan
         "http://data.europeana.eu/concept/base/214",   # Neoclassicism
         "http://data.europeana.eu/concept/base/207"    # Byzantine art
    ]
    # dynamically generte a file for each entity
    for test_entity in test_entities:
        ieb.build_individual_entity(test_entity, is_test=True)
    # compare these entities to their Mongo representation
    errors = test_files_against_mongo('dynamic')
    errors.extend(test_json_formation('dynamic'))
    return errors

# Compares stable files found in the testfiles/reference directory against
# their representation in Mongo
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
            # we need to normalise to 'def' for representing untagged string fields
            normfield = field
            if(field[-1] == "."):
                normfield = field + "def"
            elif("." not in field):
                normfield = field + ".def"
            from_xml[normfield] = vals
        # ... then of the structure in mongo
        from_mongo = {}
        mongo_rec = moclient.annocultor_db.TermList.find_one({ 'codeUri' : from_xml['id.def'][0]})
        mongo_rep = mongo_rec['representation']
        for mkey in mongo_rep.keys():
            mval = mongo_rep[mkey]
            if(type(mval) is list):
                from_mongo[mkey + ".def"] = [item for item in mval]
            elif(type(mval) is dict):
                for k, v in mval.items():
                    normfield = 'def' if k == '' else k
                    from_mongo[mkey + "." + normfield] = [item for item in mval[k]]
            else: # if single value
                from_mongo[mkey + ".def"] = [mval]
        if(from_xml['id.def'][0] == "http://data.europeana.eu/agent/base/11241"):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(from_mongo)
            print("˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜˜")
            print(from_xml)
        # TODO: now that we have our hashes, we just have to compare them
        # first, we check the fields
        missing_from_mongo = [xml_key for xml_key in from_xml.keys() if (trim_lang_tag(xml_key) in IFM.keys() and xml_to_mongo(xml_key) not in from_mongo.keys())]
        missing_from_xml = [mog_key for mog_key in from_mongo.keys() if (trim_lang_tag(mog_key) in FM.keys() and mongo_to_xml(mog_key) not in from_xml.keys())]
        # because extra prefLabels are converted to altLabels on import, we need
        # to remove irrelevant altLabels from consideration
        extra_alt_labels = [label for label in missing_from_mongo if 'skos_altLabel' in label]
        for alt_label in extra_alt_labels:
            langbit = alt_label.split(".")[1]
            pref_label = "prefLabel." + langbit
            try:
                mongo_count = len(from_mongo[alt_label])
            except:
                mongo_count = 0
            try:
                mongo_count += len(from_mongo[pref_label])
            except:
                pass
            xml_count = len(from_xml[alt_label])
            if(xml_count == (mongo_count - 1)): missing_from_mongo.remove(alt_label)
        if(len(missing_from_mongo) > 0 or len(missing_from_xml) > 0):
            entity_type = from_xml["internal_type.def"][0]
            idno = from_xml["id.def"][0]
            et = entity_type + " " + str(idno.split("/")[-1])
            msg = ["Missing from mongo: " + str(missing_from_mongo)]
            msg.append("Missing from XML: " + str(missing_from_xml))
            test_name = "Test " + filedir + " files against Mongo"
            msg = "; ".join(msg)
            sr = StatusReporter("BAD", test_name, et, msg)
            status_reports.append(sr)
    return status_reports

# Various utility functions facilitating comparison between Mongo and Solr
# entity representations
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

# check presence of mandatory fields
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
            sys.exit()
        mlogo = "Mandatory " + mfield + " field"
        disc = output_discrepancy(total_docs, mlogo, mfield_total)
        if(disc.status == "BAD"):
            errors.append(disc)
    if (len(errors) == 0):
        errors.append(StatusReporter("OK", "Mandatory Field Test", "All Entities", "All mandatory fields fully populated."))
    return errors

# every Contextual class has an attribute which it would normally be expected to have
# even though its use is not required. This function checks to ensure that representative Entities
# lacking this field in Solr are also lacking it in Mongo
def test_expected_fields():
    expected = {
        'Agent' : ['rdagr2_dateOfBirth', 'rdagr2_biographicalInformation'],
        'Place' : ['dcterms_isPartOf', 'wgs84_pos_lat', 'wgs84_pos_long'],
        'Concept' : ['skos_note']
    }
    errors = []
    x_qry = SOLR_URI.replace("rows=0", "rows=5")
    for ent_type, expected_fields in expected.items():
        for field in expected_fields:
            qm = "-" + field + ":*&fl=id&fq=" + ent_type
            qqry = x_qry + qm
            try:
                qresp = requests.get(qqry).json()['response']['docs']
            except:
                print("Test INCOMPLETE: connection to Solr server failed.")
                sys.exit()
            missings = [doc['id'] for doc in qresp]
            for missing in missings:
                mongo_field = "representation." + IFM[field]
                mqresp = moclient.annocultor_db.TermList.find_one({ "$and" :[{"codeUri" : missing }, { mongo_field : { "$exists" : True }} ]})
                if(mqresp is not None):
                    errors.append(StatusReporter("BAD", "Expected field test", missing, "Entity " + missing + " missing " + field + " field but field is present in Mongo."))
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

# test JSON is valid
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
                errors.append(StatusReporter("BAD", "JSON validity test ", entity_id, "Field " + fieldname + " with value " + text + " is not valid JSON"))
    return errors

def compare_m2s_fieldcounts():
    # gathers statistics on all populated mongo fields, solr fields
    # and outputs the result
    (mongo_entity_counter, mongo_instance_counter) = get_mongo_fieldcounts()
    (solr_entity_counter, solr_instance_counter) = get_solr_fieldcounts()
    output_fieldcounts(mongo_entity_counter, mongo_instance_counter, solr_entity_counter, solr_instance_counter)

def get_mongo_fieldcounts():
    # this is simply a deep query of the TermList collection
    mongo_count_by_entity = {}
    mongo_count_by_instance = {}
    all_records = moclient.annocultor_db.TermList.find({ "codeUri" : { "$regex" : "http://data.europeana.eu/.*" }})
    for record in all_records:
        mini_count = {}
        representation = record['representation']
        entity_type = record['entityType'].replace("Impl", "").lower()
        for slot in representation:
            t = type(representation[slot]).__name__
            if(t == 'string'):
                try:
                    mini_count[slot][entity_type] += 1
                except KeyError:
                    try:
                        mini_count[slot][entity_type] = 1
                    except KeyError:
                        mini_count[slot] = {}
                        mini_count[slot][entity_type] = 1
            if(t == 'list'):
                try:
                    mini_count[slot][entity_type] += len(representation[slot])
                except KeyError:
                    try:
                        mini_count[slot][entity_type] = len(representation[slot])
                    except KeyError:
                        mini_count[slot] = {}
                        mini_count[slot][entity_type] = len(representation[slot])
            if(t == 'dict'):
                for lang, vals in representation[slot].items():
                    att_name = slot + "." + lang
                    it = type(vals).__name__
                    inc = len(vals)
                    if(it == 'str'): inc = 1
                    try:
                        mini_count[att_name][entity_type] += inc
                    except KeyError:
                        try:
                            mini_count[att_name][entity_type] = inc
                        except KeyError:
                            mini_count[att_name] = {}
                            mini_count[att_name][entity_type] = inc
            else:   # this will be id values
                try:
                    mini_count['id'][entity_type] = 1
                except KeyError:
                    mini_count['id'] = {}
                    mini_count['id'][entity_type] = 1
        for k in mini_count.keys():
            for e in mini_count[k].keys():
                try:
                    mongo_count_by_entity[k][e] += 1
                except KeyError:
                    try:
                        mongo_count_by_entity[k][e] = 1
                    except KeyError:
                        mongo_count_by_entity[k] = {}
                        mongo_count_by_entity[k][e] = 1
                try:
                    mongo_count_by_instance[k][e] += mini_count[k][e]
                except KeyError:
                    try:
                        mongo_count_by_instance[k][e] = mini_count[k][e]
                    except KeyError:
                        mongo_count_by_instance[k] = {}
                        mongo_count_by_instance[k][e] = mini_count[k][e]
    return (mongo_count_by_entity, mongo_count_by_instance)

def get_solr_fieldcounts():
    # performs a deep scan of the solr correctly
    # and returns  a structure similar to that of
    # get_mongo_fieldcounts, above
    solr_entity_counter = {}
    solr_instance_counter = {}
    chunk_size = 250
    slr_ttl_qry = SOLR_URI + "*"
    slr_ttl = int(requests.get(slr_ttl_qry).json()['response']['numFound'])
    i = 0
    while(i < slr_ttl):
        slr_base = SOLR_URI[0:SOLR_URI.index("&")]
        slr_base += "&q=*:*&fl=*&rows=" + str(chunk_size)
        slr_chunk = slr_base + "&start=" + str(i)
        slr_r = requests.get(slr_chunk).json()
        print("Processed " + str(i) + " records")
        for doc in slr_r['response']['docs']:
            entity_type = doc['internal_type'].lower()
            field_counts = {}
            for k in doc.keys():
                try:
                    field_counts[k][entity_type] += 1
                except KeyError:
                    try:
                        field_counts[k][entity_type] = 1
                    except KeyError:
                        field_counts[k] = {}
                        field_counts[k][entity_type] = 1
            for l in field_counts.keys():
                for v in field_counts[l].keys():
                    try:
                        solr_entity_counter[l][v] += 1
                    except KeyError:
                        try:
                            solr_entity_counter[l][v] = 1
                        except KeyError:
                            solr_entity_counter[l] = {}
                            solr_entity_counter[l][v] = 1
                    try:
                        solr_instance_counter[l][v] += field_counts[l][v]
                    except KeyError:
                        try:
                            solr_instance_counter[l][v] = field_counts[l][v]
                        except KeyError:
                            solr_instance_counter[l] = {}
                            solr_instance_counter[l][v] = field_counts[l][v]
        i += chunk_size
    return (solr_entity_counter, solr_instance_counter)

def derive_solr_field_name(mongo_field_name, solr_fields):
    # given the name of a mongo field in Annocultor DB
    # derives the name of the corresponding field in Solr
    errmsg = "NOT FOUND"
    if("." in mongo_field_name):
        unq_mongo_field_name = mongo_field_name[:mongo_field_name.index(".")]
        solr_field_name = FM[unq_mongo_field_name]
        langq = mongo_field_name[mongo_field_name.index(".") + 1:]
        if((solr_field_name + "." + langq) in solr_fields):
            return solr_field_name + "." + langq
        elif(solr_field_name in solr_fields):
            return solr_field_name
        else:
            return errmsg
    else:
        try:
            return FM[mongo_field_name]
        except KeyError:
            return errmsg

def get_typed_count(typed_hash, entity_type='all'):
    # returns the count for a given entity type (agent|concept|place)
    # or sums counts for each item type if a combined total is desired
    if(entity_type == "all"):
        total = 0
        for k, v in typed_hash.items():
            total += v
        return total
    else:
        if entity_type in typed_hash.keys():
            return typed_hash[entity_type]
        else:
            return 0

def output_fieldcount_by_entity(mongo_entity_counter, mongo_instance_counter, solr_entity_counter, solr_instance_counter, entity_type='all'):
    filename = entity_type + "_fieldcount_report.log"
    filepath =  os.path.join(os.path.dirname(__file__), '..', 'logs', 'import_tests', filename)
    with open(filepath, 'w') as fr:
        # Outputs a side-by-side comparison of the Mongo and Solr Entity Collection
        # fields and their degree of population.
        fr.write("COMPARISON BY ENTITY:\nMONGO\t\t\t\t\tMONGO COUNT\t\tSOLR\t\t\t\t\tSOLR COUNT\n")
        fr.write("==================================================================================================\n")
        for mongo_field_name in sorted(mongo_entity_counter.keys()):
            mongo_count = get_typed_count(mongo_entity_counter[mongo_field_name], entity_type)
            solr_field_name = derive_solr_field_name(mongo_field_name, solr_entity_counter.keys())
            try:
                solr_count = get_typed_count(solr_entity_counter[solr_field_name], entity_type)
            except KeyError:
                solr_count = "FIELD NOT FOUND"
            if(mongo_count == 0 and (solr_count == 0 or solr_count == "FIELD NOT FOUND")):
                continue
            fr.write(mongo_field_name + "\t\t" + str(mongo_count) + "\t\t" + solr_field_name + "\t\t" + str(solr_count))
            fr.write("\n")
        fr.write("\n\nCOMPARISON BY FIELD:\nMONGO\t\t\t\t\tMONGO COUNT\t\tSOLR\t\t\t\t\tSOLR COUNT\n")
        fr.write("==================================================================================================\n")
        for mongo_field_name in sorted(mongo_instance_counter.keys()):
            mongo_count = get_typed_count(mongo_instance_counter[mongo_field_name], entity_type)
            solr_field_name = derive_solr_field_name(mongo_field_name, solr_entity_counter.keys())
            try:
                solr_count = get_typed_count(solr_instance_counter[solr_field_name], entity_type)
            except KeyError:
                solr_count = "FIELD NOT FOUND"
            if(mongo_count == 0 and (solr_count == 0 or solr_count == "FIELD NOT FOUND")): continue
            fr.write(mongo_field_name + "\t\t" + str(mongo_count) + "\t\t" + solr_field_name + "\t\t" + str(solr_count))
            fr.write("\n")
        if(entity_type == "all"):
            untranslatable_mongo_fields = set([k.split(".")[0] for k in mongo_entity_counter.keys() if k.split(".")[0] not in FM.keys()])
            untranslatable_solr_fields = set([k.split(".")[0] for k in solr_entity_counter.keys() if k.split(".")[0] not in IFM.keys()])
            if(len(untranslatable_mongo_fields) > 0):
                fr.write("\nUntranslatable Mongo Fields: " + str(untranslatable_mongo_fields) + "\n")
            if(len(untranslatable_solr_fields) > 0):
                fr.write("\nUntranslatable Solr Fields: " + str(untranslatable_solr_fields) + "\n")


def output_fieldcounts(mongo_entity_counter, mongo_instance_counter, solr_entity_counter, solr_instance_counter):
    for et in ALL_ENT_TYPES:
        output_fieldcount_by_entity(mongo_entity_counter, mongo_instance_counter, solr_entity_counter, solr_instance_counter, et)


def run_test_suite(suppress_stdout=False, log_to_file=False):
    errors = []
    errors.extend(test_totals())
    errors.extend(test_transform())
    errors.extend(test_against_reference())
    errors.extend(test_mandatory_fields())
    errors.extend(test_expected_fields())
    errors.extend(test_files_against_mongo())
    for error in errors: error.display(suppress_stdout, log_to_file)

# generates a list of all IDs found in Mongo but not in Solr and writes it to file
def report_filecount_discrepancy():
    all_mongo_ids = []
    all_solr_ids = []
    all_records = moclient.annocultor_db.TermList.find({ "codeUri" : { "$regex" : "http://data.europeana.eu/.*" }})
    count = 0
    for record in all_records:
        try:
            all_mongo_ids.append(record['codeUri'])
        except:
            pass
        count += 1
        if(count % 10000 == 0): print(str(count) + " Mongo records processed.")
    solr_count = get_solr_total()
    query_block = 250
    for i in range(0, int(solr_count) + query_block, query_block):
        qry = SOLR_URI + "*:*&fl=id&rows=" + str(query_block) + "&start=" + str(i)
        qry = qry.replace("&rows=0", "")
        try:
            resp = requests.get(qry).json()
            for doc in resp['response']['docs']:
                all_solr_ids.append(doc['id'])
        except:
            print("Test INCOMPLETE: connection to Solr server failed.")
            print(missing_ids)
            with open(filepath, 'w') as missids:
                for id in missing_ids: missids.write(id + "\n")
            sys.exit()
        if(i % 10000 == 0 and i > 0): print(str(i) + " Solr records processed.")
    missing_ids = set(all_mongo_ids).difference(set(all_solr_ids))
    filepath =  os.path.join(os.path.dirname(__file__), '..', 'logs', 'import_tests', 'missing_entities.log')
    with open(filepath, 'w') as missids:
        for id in missing_ids: missids.write(id + "\n")

# generates a list of Solr documents missing the passed field, and writes it to file
def report_missing_fields(fieldname):
    # to avoid an expensive query, we first check whether *any* documents have
    # the field in question, or if *all* of them do.
    all = "*:*"
    all_qry = SOLR_URI  + all
    try:
        all_count = requests.get(all_qry).json()['response']['numFound']
    except:
        print("Test INCOMPLETE: connection to Solr server failed.")
        sys.exit()
    trm = "-" + fieldname + ":*"
    qry = SOLR_URI + trm
    try:
        qual_count = requests.get(qry).json()['response']['numFound']
    except:
        print("Test INCOMPLETE: connection to Solr server failed.")
        sys.exit()
    strt_message = ""
    if(qual_count == all_count):
        strt_message = "All documents missing field " + str(fieldname) + "\n"
    elif(qual_count == 0):
        strt_message = "Field " + fieldname + " exists on all documents.\n"
    filename = str(fieldname) + "_report.log"
    filepath =  os.path.join(os.path.dirname(__file__), '..', 'logs', 'import_tests', filename)
    with open(filepath, 'w') as report:
        report.write(strt_message)
        if(qual_count > 0 and qual_count < all_count):
            missing = []
            ntrm = "-" + fieldname + ":*"
            nqry = SOLR_URI + ntrm
            query_block = 250
            nqry = nqry.replace("rows=0", "rows=" + str(query_block))
            for i in range(0, int(qual_count + query_block), query_block):
                mnqry = nqry + "&start=" + str(i)
                try:
                    nresp = requests.get(mnqry).json()
                except:
                    print("Test INCOMPLETE: connection to Solr server failed.")
                    for missing_id in missing: report.write(missing_id + "\n")
                    sys.exit()
                for doc in nresp['response']['docs']:
                    missing.append(doc['id'])
            for missing_id in missing: report.write(missing_id + "\n")
