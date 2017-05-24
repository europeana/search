class LanguageValidator:
    import sys, os
    # TODO: What to do with weird 'def' language tags all over the place?
    LOG_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'logs', 'langlogs')

    def __init__(self):
        import os
        self.langmap = {}
        langlistloc = os.path.join(os.path.dirname(__file__), '..', 'all_langs.wkp')
        with open(langlistloc, 'r') as all_langs:
            for lang in all_langs:
                if(not(lang.startswith("#")) and ("|" in lang)):
                    (name, code) = lang.split('|')
                    self.langmap[code.strip()] = name

    def validate_lang_code(self, entity_id, code):
       if(code in self.langmap.keys()):
           return True
       elif(code == 'def'):
           # TODO: sort out the 'def' mess at some point
           self.log_invalid_lang_code(entity_id, 'def')
           return True
       elif(code == ''):
           self.log_invalid_lang_code(entity_id, 'Empty string')
           return True
       else:
           self.log_invalid_lang_code(entity_id, code)
           return False

    def pure_validate_lang_code(self, code):
       if(code in self.langmap.keys()):
           return True
       elif(code == 'def'):
           return True
       else:
           return False

    def log_invalid_lang_code(self, entity_id, code):
        # TODO: differentiate logfiles by date
        filename = "logs.txt"
        filepath = LanguageValidator.LOG_LOCATION + filename
        with open(filepath, 'a') as lgout:
            msg = "Invalid language code found on entity " + str(entity_id) + ": " + str(code)
            lgout.write(msg)
            lgout.write("\n")

    def print_langs(self):
        print(self.langmap)

class ContextClassHarvester:

    import os

    MONGO_HOST = 'mongodb://136.243.103.29'
    MONGO_PORT = 27017
    CHUNK_SIZE = 250   # each file will consist of 250 entities
    WRITEDIR = os.path.join(os.path.dirname(__file__), '..', 'entities_out')
    LANG_VALIDATOR = LanguageValidator()
    LOG_LOCATION = 'logs/entlogs/'
    FIELD_MAP = {
        # maps mongo fields to their solr equivalents
        'prefLabel' : { 'label' : 'skos_prefLabel' , 'type' : 'string' },
        'altLabel' : { 'label': 'skos_altLabel' , 'type' : 'string' },
        'note' : { 'label': 'skos_note' , 'type' : 'string' },
        'owlSameAs' : { 'label': 'owl_sameAs' , 'type' : 'ref' },
        'edmIsRelatedTo' : { 'label': 'edm_isRelatedTo' , 'type' : 'ref' },
        'dcIdentifier' : { 'label': 'dc_identifier' , 'type' : 'string' },
        'rdaGr2DateOfBirth' : { 'label': 'rdagr2_dateOfBirth' , 'type' : 'string' },
        'rdaGr2DateOfDeath' : { 'label': 'rdagr2_dateOfDeath' , 'type' : 'string' },
        'rdaGr2PlaceOfBirth' : { 'label': 'rdagr2_placeOfBirth' , 'type' : 'string' },
        'rdaGr2PlaceOfDeath' : { 'label': 'rdagr2_placeOfDeath' , 'type' : 'string' },
        'rdaGr2ProfessionOrOccupation' :  { 'label': 'rdagr2_professionOrOccupation' , 'type' : 'string' },
        'rdaGr2BiographicalInformation' : { 'label': 'rdagr2_biographicalInformation' , 'type' : 'string' },
        'latitude' : { 'label': 'wgs84_pos_lat' , 'type' : 'string' },
        'longitude' : { 'label': 'wgs84_pos_long' , 'type' : 'string' },
        'begin' : { 'label': 'edm_begin' , 'type' : 'string' },
        'end' : { 'label': 'edm_end' , 'type' : 'string' },
        'isPartOf' : { 'label': 'dcterms_isPartOf' , 'type' : 'ref' },
        'hasMet' : { 'label' : 'edm_hasMet', 'type' : 'ref' },
        'date' : { 'label' : 'dc_date', 'type' : 'string' },
        'exactMatch': { 'label' :  'skos_exactMatch', 'type' : 'string' },
        'related' : { 'label' : 'skos_related', 'type' : 'ref'  }

    }

    def __init__(self, name, entity_class):
        from pymongo import MongoClient
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'preview_builder'))
        import RelevanceCounter
        import PreviewBuilder

        self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        self.write_dir = ContextClassHarvester.WRITEDIR + "/" + self.name
        self.preview_builder = PreviewBuilder.PreviewBuilder()

    def build_solr_doc(self, entities, start):
        from xml.etree import ElementTree as ET

        docroot = ET.Element('add')
        for entity_id, values  in entities.items():
            self.build_entity_doc(docroot, entity_id, values)
        self.client.close()
        return self.write_to_file(docroot, start)

    def add_field(self, docroot, field_name, field_value):
        from xml.etree import ElementTree as ET

        f = ET.SubElement(docroot, 'field')
        f.set('name', field_name)
        try:
            f.text = self.sanitize_field(field_value)
        except Exception as ex:
            print(str(field_name) + "!" + str(field_value) + str(ex))

    def sanitize_field(self, field_value):
        field_value = field_value.replace("\n", " ")
        field_value = field_value.replace("\\n", " ")
        return field_value

    def write_to_file(self, doc, start):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom
        import io
        writepath = self.get_writepath(start)
        roughstring = ET.tostring(doc, encoding='utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
        with io.open(writepath, 'w', encoding='utf-8') as writefile:
            writefile.write(reparsed)
            writefile.close()
        return writepath

    def get_writepath(self, start):
        return self.write_dir + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows):
        hitcounts = self.relevance_counter.get_raw_relevance_metrics(entity_id, entity_rows)
        eu_enrichments = hitcounts["europeana_enrichment_hits"]
        eu_terms = hitcounts["europeana_string_hits"]
        pagerank = hitcounts["pagerank"]
        ds = self.relevance_counter.calculate_relevance_score(pagerank, eu_enrichments, eu_terms)
        self.add_field(docroot, 'europeana_doc_count', str(eu_enrichments))
        self.add_field(docroot, 'europeana_term_hits', str(eu_terms))
        self.add_field(docroot, 'pagerank', str(pagerank))
        self.add_field(docroot, 'derived_score', str(ds))
        self.add_suggest_filters(docroot, eu_terms)
        return True

    def process_representation(self, docroot, entity_id, entity_rows):
        import json
        all_preflabels = []
        for characteristic in entity_rows['representation']:
            if str(characteristic) not in ContextClassHarvester.FIELD_MAP.keys():
                # TODO: log this?
                continue
                # if the entry is a dictionary, then the keys should be language codes
            if(type(entity_rows['representation'][characteristic]) is dict):
                for lang in entity_rows['representation'][characteristic]:
                    pref_label_count = 0
                    prev_alts = []
                    if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(entity_id, lang)):
                        field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                        field_values = entity_rows['representation'][characteristic][lang]
                        for field_value in field_values:
                            q_field_name = field_name
                            unq_name = lang if lang != 'def' else ''
                            if(ContextClassHarvester.FIELD_MAP[characteristic]['type'] == 'string'):
                                q_field_name = field_name + "."+ unq_name
                            # Code snarl: we often have more than one prefLabel per language in the data
                            # We can also have altLabels
                            # We want to shunt all but the first-encountered prefLabel into the altLabel field
                            # while ensuring the altLabels are individually unique
                            # TODO: Refactor (though note that this is a non-trivial refactoring)
                            if(characteristic == 'prefLabel' and pref_label_count > 0):
                                q_field_name = "skos_altLabel." + unq_name
                            if('altLabel' in q_field_name):
                                if(field_value in prev_alts):
                                    continue
                                prev_alts.append(field_value)
                            self.add_field(docroot, q_field_name, field_value)
                            if(characteristic == 'prefLabel' and pref_label_count == 0 and unq_name != ""):
                                pref_label_count = 1
                                all_preflabels.append(field_value)
            elif(type(entity_rows['representation'][characteristic]) is list):
                field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                for entry in entity_rows['representation'][characteristic]:
                    self.add_field(docroot, field_name, entry)
            else: # if a single value
                try:
                    field_name = ContextClassHarvester.FIELD_MAP[characteristic]['label']
                    field_value = entity_rows['representation'][characteristic]
                    self.add_field(docroot, field_name, str(field_value))
                except KeyError as ke:
                    print('Attribute ' + field_name + ' found in source but undefined in schema.')
        payload = self.build_payload(entity_id, entity_rows)
        self.add_field(docroot, 'payload', json.dumps(payload))
        self.add_field(docroot, 'skos_prefLabel', " ".join(sorted(set(all_preflabels))))
        depiction = self.preview_builder.get_depiction(entity_id)
        if(depiction is not None):
            self.add_field(docroot, 'foaf_depiction', depiction)
        self.grab_relevance_ratings(docroot, entity_id, entity_rows['representation'])

    #def add_label_payload(self, entity_id, entity_rows, language, payload_accumulator):
    #    import json
    #    type = entity_rows['entityType'].replace('Impl', '')
    #    payload = self.preview_builder.build_label_preview(type, entity_id, entity_rows, language)
    #    payload_accumulator[language] = payload

    def build_payload(self, entity_id, entity_rows):
        import json
        entity_type = entity_rows['entityType'].replace('Impl', '')
        payload = self.preview_builder.build_preview(entity_type, entity_id, entity_rows['representation'])
        return payload

    def add_suggest_filters(self, docroot, term_hits):
        entity_type = self.name[0:len(self.name) - 1].capitalize()
        self.add_field(docroot, 'suggest_filters', entity_type)
        if(term_hits > 0):
            self.add_field(docroot, 'suggest_filters', 'in_europeana')

class ConceptHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        ContextClassHarvester.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        self.relevance_counter = RelevanceCounter.ConceptRelevanceCounter()

    def get_entity_count(self):
        concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )
        return len(concepts)

    def build_entity_chunk(self, start):
        concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        concepts_chunk = {}
        for concept in concepts:
            concepts_chunk[concept] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : concept })
        return concepts_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        id = entity_rows['codeUri']
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Concept')
        self.process_representation(doc, id, entity_rows)

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        self.relevance_counter = RelevanceCounter.AgentRelevanceCounter()

    def get_entity_count(self):
        agents = self.client.annocultor_db.people.distinct( 'codeUri' )
        return len(agents)

    def build_entity_chunk(self, start):
        agents = self.client.annocultor_db.people.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        agents_chunk = {}
        for agent in agents:
            agents_chunk[agent] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : agent })
        return agents_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        if(entity_rows is None):
            self.log_missing_entry(entity_id)
            return
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Agent')
        self.process_representation(doc, entity_id, entity_rows)

    def log_missing_entry(self, entity_id):
        msg = "Entity found in Agents but not TermList collection: " + entity_id
        logfile = "missing_agents.txt"
        logpath = ContextClassHarvester.LOG_LOCATION + logfile
        with open(logpath, 'a') as lgout:
            lgout.write(msg)
            lgout.write("\n")


class PlaceHarvester(ContextClassHarvester):

    def __init__(self):
        import sys, os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'places', 'eu.europeana.corelib.solr.entity.PlaceImpl')
        self.relevance_counter = RelevanceCounter.PlaceRelevanceCounter()

    def get_entity_count(self):
        place_list = self.client.annocultor_db.TermList.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/place/).*$' }} )
        return len(place_list)

    def build_entity_chunk(self, start):
        places = self.client.annocultor_db.place.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        places_chunk = {}
        for place in places:
            places_chunk[place] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : place })
        return places_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', id)
        self.add_field(doc, 'internal_type', 'Place')
        self.process_representation(doc, entity_id, entity_rows)

class IndividualEntityBuilder:
    import os, shutil

    TESTDIR = os.path.join(os.path.dirname(__file__), '..', 'tests', 'testfiles', 'dynamic')

    def build_individual_entity(self, entity_id, is_test=False):
        from pymongo import MongoClient
        import os, shutil
        self.client = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        entity_rows = self.client.annocultor_db.TermList.find_one({ "codeUri" : entity_id })
        entity_chunk = {}
        entity_chunk[entity_id] = entity_rows
        rawtype = entity_rows['entityType']
        if(rawtype == 'PlaceImpl'):
            harvester = PlaceHarvester()
        elif(rawtype == 'AgentImpl'):
            harvester = AgentHarvester()
        else:
            harvester = ConceptHarvester()
        start = int(entity_id.split("/")[-1])
        harvester.build_solr_doc(entity_chunk, start)
        if(not(is_test)): print("Entity " + entity_id + " written to " + rawtype[0:-4].lower() + "_" + str(start) + ".xml file.")
        if(is_test):
            current_location = harvester.get_writepath(start)
            namebits = entity_id.split("/")
            newname = namebits[-3] + "_" + namebits[-1] + ".xml"
            shutil.copyfile(current_location, IndividualEntityBuilder.TESTDIR + "/" + newname)
            os.remove(current_location) # cleaning up
#        except Exception as e:
#            print("No entity with that ID found in database. " + str(e))
#            return

class ChunkBuilder:

    def __init__(self, entity_type, start):
        self.entity_type = entity_type.lower()
        self.start = start

    def build_chunk(self):
        harvester = ConceptHarvester()
        if(self.entity_type == "agent"):
            harvester = AgentHarvester()
        elif(self.entity_type == "place"):
            harvester = PlaceHarvester()
        ec = harvester.build_entity_chunk(self.start)
        harvester.build_solr_doc(ec, self.start)
