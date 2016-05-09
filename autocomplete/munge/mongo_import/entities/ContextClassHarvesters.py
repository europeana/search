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
       else:
           code = code if code != '' else 'No code provided'
           self.log_invalid_lang_code(entity_id, code)
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
    CHUNK_SIZE = 1000
    WRITEDIR = getcwd() + '/../entities_out'
    LANG_VALIDATOR = LanguageValidator()
    LOG_LOCATION = '../logs/entlogs/'

    def __init__(self, name, entity_class):
        from pymongo import MongoClient
        import sys
        sys.path.append('ranking_metrics')
        import RelevanceCounter

        self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        self.wpedia_rc = RelevanceCounter.WpediaRelevanceCounter()
        self.euro_rc = RelevanceCounter.EuDocRelevanceCounter()
        self.write_dir = ContextClassHarvester.WRITEDIR + "/" + self.name

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
            concepts_chunk[concept] = self.client.annocultor_db.concept.find({ 'codeUri' : concept })
        return concepts_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET

        doc = ET.SubElement(docroot, 'doc')
        id = entity_rows[0]['codeUri']
        self.add_field(doc, 'entity_id', id)
        self.add_field(doc, 'internal_type', 'Concept')
        euc_count = self.euro_rc.get_new_term_count(id)
        for now_doc in entity_rows:
            lang = now_doc['lang'] if 'lang' in now_doc else ''
            if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(id, lang)):
                label = now_doc['label'] if 'label' in now_doc else ''
                if(lang == "en"):
                    wpc_count = self.wpedia_rc.get_new_term_count(label)
                    self.add_field(doc, 'europeana_doc_count', str(euc_count))
                    self.add_field(doc, 'wikipedia_clicks', str(wpc_count))
                    ds = self.euro_rc(euc_count, wpc_count)
                    self.add_field(doc, 'derived_score', str(ds))
                    field_name = "skos_prefLabel." + lang
                    self.add_field(doc, field_name, label)

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        import sys
        sys.path.append('ranking_metrics')
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        self.ag_rc = RelevanceCounter.AgentRelevanceCounter()
        self.legacy_mongo = MongoClient('mongodb://mongo1.eanadev.org', ContextClassHarvester.MONGO_PORT)

    def get_entity_count(self):
        agents = self.client.annocultor_db.people.distinct( 'codeUri' )
        return len(agents)

    def build_entity_chunk(self, start):
        from pymongo import MongoClient
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

    def process_representation(self, docroot, entity_id, entity_rows):
        field_map = {}
        field_map['prefLabel'] = 'skos_prefLabel'
        field_map['altLabel'] = 'skos_altLabel'
        # TODO: Expand for additional related fields
        if('representation' in entity_rows):
            for characteristic in entity_rows['representation']:
                if(characteristic in field_map.keys()):
                    for lang in entity_rows['representation'][characteristic]:
                        if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(entity_id, lang)):
                            field_name = field_map[characteristic]
                            field_values = entity_rows['representation'][characteristic][lang]
                            for field_value in field_values:
                                qual_field_name = field_name + "." + lang
                                self.add_field(docroot, field_name, field_value)
                                self.add_field(docroot, qual_field_name, field_value)
            if('owlSameAs' in entity_rows['representation']):
                self.grab_relevance_ratings(docroot, entity_rows['representation']['owlSameAs'])
            else:
                self.assign_zero_relevance(docroot)
        else:
            return

    def grab_relevance_ratings(self, docroot, sames):
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
        self.legacy_mongo = MongoClient('mongodb://mongo1.eanadev.org', ContextClassHarvester.MONGO_PORT)
        self.place_ids = []
        for key, value in self.pl_rc.freqs.items():
            self.place_ids.append(key)

    def get_entity_count(self):
        return len(self.place_ids)

    def build_entity_chunk(self, start):
        places = {}
        i = 0
        for place_id in self.place_ids[start:start + ContextClassHarvester.CHUNK_SIZE]:
            place = self.client.annocultor_db.Place.find_one({ 'about' : place_id })
            if(place is not None):
                places[i] = place
                i += 1
        return places

    def build_entity_doc(self, docroot, entity_id, entity):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity['about']
        hitcount = self.pl_rc.get_term_count(id)
        eu_count = hitcount['eu_df']
        wk_count_90_days = hitcount['wpedia_clicks']
        if(eu_count > 0): # filter out all entities not found in our collections (doh!)
            doc = ET.SubElement(docroot, 'doc')
            self.add_field(doc, 'entity_id', id)
            self.add_field(doc, 'internal_type', 'Place')
            self.add_field(doc, 'europeana_doc_count', str(eu_count))
            wk_count_annual = wk_count_90_days * 4 # an approximation is good enough here
            self.add_field(doc, 'wikipedia_clicks', str(wk_count_annual))
            ds = self.pl_rc.calculate_relevance_score(eu_count, wk_count_annual)
            self.add_field(doc, 'derived_score', str(wk_count_annual * eu_count))
            for lang_code, label_list in entity['prefLabel'].items():
                # we need to workaround 'def', though it's unclear why
                if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(id, lang_code) or lang_code == 'def'):
                    suffix = '.' + lang_code if lang_code != 'def' else ''
                    tagname = 'skos_prefLabel' + suffix
                    for label in label_list:
                        self.add_field(doc, tagname, label)



