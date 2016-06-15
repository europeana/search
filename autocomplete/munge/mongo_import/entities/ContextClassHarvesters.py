class LanguageValidator:
    # TODO: What to do with weird 'def' language tags all over the place?
    LOG_LOCATION = "../logs/langlogs/"

    def __init__(self):
        self.langmap = {}
        with open('../all_langs.wkp', 'r') as all_langs:
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
       else:
           code = code if code != '' else 'No code provided'
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

    from os import getcwd

    MONGO_HOST = 'mongodb://136.243.103.29'
    MONGO_PORT = 27017
    LEGACY_MONGO_HOST = 'mongodb://mongo1.eanadev.org'

    CHUNK_SIZE = 1000
    WRITEDIR = getcwd() + '/../entities_out'
    LANG_VALIDATOR = LanguageValidator()
    LOG_LOCATION = '../logs/entlogs/'

    def __init__(self, name, entity_class):
        from pymongo import MongoClient
        import sys
        sys.path.append('ranking_metrics')
        sys.path.append('preview_builder')
        import RelevanceCounter
        import PreviewBuilder

        self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        self.wpedia_rc = RelevanceCounter.WpediaRelevanceCounter()
        self.euro_rc = RelevanceCounter.EuDocRelevanceCounter()
        self.write_dir = ContextClassHarvester.WRITEDIR + "/" + self.name
        self.preview_builder = PreviewBuilder.PreviewBuilder()
        self.populate_field_map()

    def populate_field_map(self):
        # maps field names in Mongo to Solr schema field names
        # the convention for Solr names is to retain the names from the
        # Production schema, but drop the entity-type prefixes
        self.field_map = {}
        self.field_map['prefLabel'] = 'skos_prefLabel'
        self.field_map['altLabel'] = 'skos_altLabel'
        self.field_map['note'] = 'skos_note'
        self.field_map['owlSameAs'] = 'owl_sameAs'
        self.field_map['edmIsRelatedTo'] = 'skos_isRelatedTo'
        self.field_map['dcIdentifier'] = 'dc_identifier'
        self.field_map['rdaGr2DateOfBirth'] = 'rdagr2_dateOfBirth'
        self.field_map['rdaGr2DateOfDeath'] = 'rdagr2_dateOfDeath'
        self.field_map['rdaGr2PlaceOfBirth'] = 'rdagr2_placeOfBirth'
        self.field_map['rdaGr2PlaceOfDeath'] = 'rdagr2_placeOfDeath'
        self.field_map['rdaGr2ProfessionOrOccupation'] = 'rdagr2_professionOrOccupation'
        self.field_map['rdaGr2BiographicalInformation'] = 'rdagr2_biographicalInformation'
        self.field_map['end'] = 'edm_end'
        self.field_map['isPartOf'] = 'skos_isPartOf'

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
            f.text = field_value
        except Exception as ex:
            print(field_name + "!" + field_value + str(ex))

    def write_to_file(self, doc, start):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom
        import io

        writepath = self.write_dir + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"
        roughstring = ET.tostring(doc, encoding='utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
        with io.open(writepath, 'w', encoding='utf-8') as writefile:
            writefile.write(reparsed)
            writefile.close()
        return writepath

    def process_representation(self, docroot, entity_id, entity_rows):
        for characteristic in entity_rows['representation']:
            if str(characteristic) not in self.field_map.keys():
                # TODO: log this?
                continue
                # if the entry is a dictionary, then the keys should be language codes
            if(type(entity_rows['representation'][characteristic]) is dict):
                for lang in entity_rows['representation'][characteristic]:
                    if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(entity_id, lang)):
                        field_name = self.field_map[characteristic]
                        field_values = entity_rows['representation'][characteristic][lang]
                        for field_value in field_values:
                            qual_field_name = field_name + "." + lang
                            # self.add_field(docroot, field_name, field_value) # do this with copyfields
                            self.add_field(docroot, qual_field_name, field_value)
            elif(type(entity_rows['representation'][characteristic]) is list):
                field_name = self.field_map[characteristic]
                for entry in entity_rows['representation'][characteristic]:
                    self.add_field(docroot, field_name, entry)
        # TODO: find a better design pattern for calling grab_relevance_ratings
        sames = None if 'owlSameAs' not in entity_rows['representation'] else entity_rows['representation']['owlSameAs']
        self.grab_relevance_ratings(docroot, entity_id, entity_rows['representation'], sames)
        raw_type = entity_rows['entityType'].replace('Impl', '')
        payload = self.preview_builder.build_preview(raw_type, entity_id, entity_rows)
        self.add_field(docroot, 'payload', payload)

class ConceptHarvester(ContextClassHarvester):

    def __init__(self):
        ContextClassHarvester.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')

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
        self.add_field(doc, 'entity_id', id)
        self.add_field(doc, 'internal_type', 'Concept')
        self.process_representation(doc, id, entity_rows)

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows, sames):
        wpc_count = 0
        euc_count = self.euro_rc.get_new_term_count(entity_id)
        ds = 0
        if 'prefLabel' in entity_rows.keys() and 'en' in entity_rows['prefLabel'].keys():
            label = entity_rows['prefLabel']['en'][0]
            wpc_count = self.wpedia_rc.get_new_term_count(label)
            ds = self.euro_rc.calculate_relevance_score(euc_count, wpc_count)
        self.add_field(docroot, 'derived_score', str(ds))
        self.add_field(docroot, 'europeana_doc_count', str(euc_count))
        self.add_field(docroot, 'wikipedia_clicks', str(wpc_count))

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        import sys
        sys.path.append('ranking_metrics')
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        self.ag_rc = RelevanceCounter.AgentRelevanceCounter()

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
        self.add_field(doc, 'entity_id', id)
        self.add_field(doc, 'internal_type', 'Agent')
        self.process_representation(doc, entity_id, entity_rows)

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows, sames):
        import re
        for same in sames:
            if(re.match('http://dbpedia.org/resource/.+', same )):
                hitcounts = self.ag_rc.get_term_count(same)
                wpedia_clicks = hitcounts["wpedia_clicks"] if "wpedia_clicks" in hitcounts else -1
                eu_df = hitcounts["eu_df"] if "eu_df" in hitcounts else 0
                eu_df = eu_df if(eu_df != -1) else 0
                ds = self.ag_rc.calculate_relevance_score(eu_df, wpedia_clicks)
                self.add_field(docroot, 'europeana_doc_count', str(eu_df))
                self.add_field(docroot, 'wikipedia_clicks', str(wpedia_clicks))
                self.add_field(docroot, 'derived_score', str(ds))
                return True # we don't want more than one relevance ranking
        # if no match is found, relevance score is 0
        self.assign_zero_relevance(docroot)
        return False

    def assign_zero_relevance(self, docroot):
        self.add_field(docroot, 'europeana_doc_count', '0')
        self.add_field(docroot, 'wikipedia_clicks', '0')
        self.add_field(docroot, 'derived_score', '0')

    def log_missing_entry(self, entity_id):
        msg = "Entity found in Agents but not TermList collection: " + entity_id
        logfile = "missing_agents.txt"
        logpath = ContextClassHarvester.LOG_LOCATION + logfile
        with open(logpath, 'a') as lgout:
            lgout.write(msg)
            lgout.write("\n")

class PlaceHarvester(ContextClassHarvester):

    def __init__(self):
        import sys
        sys.path.append('ranking_metrics')
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'places', 'eu.europeana.corelib.solr.entity.PlaceImpl')
        self.pl_rc = RelevanceCounter.PlaceRelevanceCounter()
        self.place_ids = []
        for key, value in self.pl_rc.freqs.items():
            self.place_ids.append(key)

    def get_entity_count(self):
        return len(self.place_ids)

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
        hitcount = self.pl_rc.get_term_count(id)
        eu_count = hitcount['eu_df']
        wk_count_90_days = hitcount['wpedia_clicks']
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'entity_id', id)
        self.add_field(doc, 'internal_type', 'Place')
        self.add_field(doc, 'europeana_doc_count', str(eu_count))
        wk_count_annual = wk_count_90_days * 4 # an approximation is good enough here
        self.add_field(doc, 'wikipedia_clicks', str(wk_count_annual))
        ds = self.pl_rc.calculate_relevance_score(eu_count, wk_count_annual)
        self.add_field(doc, 'derived_score', str(wk_count_annual * eu_count))
        self.process_representation(doc, entity_id, entity_rows)

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows, sames):
        hitcounts = self.pl_rc.get_term_count(entity_id)
        wpedia_clicks = hitcounts["wpedia_clicks"] if "wpedia_clicks" in hitcounts else -1
        eu_df = hitcounts["eu_df"] if "eu_df" in hitcounts else 0
        eu_df = eu_df if(eu_df != -1) else 0
        ds = self.pl_rc.calculate_relevance_score(eu_df, wpedia_clicks)
        self.add_field(docroot, 'europeana_doc_count', str(eu_df))
        self.add_field(docroot, 'wikipedia_clicks', str(wpedia_clicks))
        self.add_field(docroot, 'derived_score', str(ds))
        return True

