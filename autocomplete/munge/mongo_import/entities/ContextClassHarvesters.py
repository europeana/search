class ContextClassHarvester:

    from os import getcwd

    MONGO_HOST = 'mongodb://136.243.103.29'
    MONGO_PORT = 27017
    CHUNK_SIZE = 1000
    WRITEDIR = getcwd() + '/../entities_out'

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

        writepath = self.write_dir + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"
        roughstring = ET.tostring(doc, encoding='utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
        with open(writepath, 'w') as writefile:
            writefile.write(reparsed.encode('utf-8'))
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
            lang = "." + now_doc['lang'] if 'lang' in now_doc else ''
            label = now_doc['label'] if 'label' in now_doc else ''
            if(lang == ".en"):
                wpc_count = self.wpedia_rc.get_new_term_count(label)
                self.add_field(doc, 'europeana_doc_count', str(euc_count))
                self.add_field(doc, 'wikipedia_clicks', str(wpc_count))
                tmp_wpc_count = abs(wpc_count)
                ds = euc_count * tmp_wpc_count
                self.add_field(doc, 'derived_score', str(ds))
            field_name="skos_prefLabel" + lang
            self.add_field(doc, field_name, label)

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        import sys
        sys.path.append('ranking_metrics')
        import RelevanceCounter
        from pymongo import MongoClient
        ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        self.ag_rc = RelevanceCounter.AgentRelevanceCounter()
        self.legacy_mongo = MongoClient('mongodb://mongo2.eanadev.org', ContextClassHarvester.MONGO_PORT)

    def get_entity_count(self):
        agents = self.client.annocultor_db.people.distinct( 'codeUri' )
        return len(agents)

    def build_entity_chunk(self, start):
        from pymongo import MongoClient
        agents = self.client.annocultor_db.people.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        agents_chunk = {}
        for agent in agents:
            new_agent_id = self.client.annocultor_db.lookup.find_one({ 'codeUri' : agent })
            try:
                legacy_agent_id = new_agent_id['originalCodeUri']
                agent_record = self.legacy_mongo.europeana.Agent.find({ 'about' : legacy_agent_id})
                if(agent_record.count() == 0): raise KeyError
                agents_chunk[agent] = agent_record
            except Exception as e:
                agent_record = self.client.annocultor_db.people.find({ 'codeUri' : agent })
                agents_chunk[agent] = agent_record
        return agents_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        import sys
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        id = entity_id
        doc = ET.SubElement(docroot, 'doc')
        if(entity_rows.count() > 0 and 'about' in entity_rows[0]):
            self.build_legacy_doc(doc, entity_rows[0])
        else:
            self.build_current_doc(doc, entity_rows)
        self.add_field(doc, 'entity_id', id)
        self.add_field(doc, 'internal_type', 'Agent')

    def build_current_doc(self, document, entity_rows):
        langdict = {}
        for item in entity_rows:
            lang = item['lang']
            label = item['label']
            if(lang not in langdict):
                langdict[lang] = list()
                langdict[lang].append(label)
            else:
                langdict[lang].append(label)
        for lang, label_list in langdict.items():
            self.add_field(document, "skos_prefLabel." + lang, label_list.pop(0))
            for label in label_list:
                self.add_field(document, "skos_altLabel." + lang, label)
        self.add_field(document, 'europeana_doc_count', '0')
        self.add_field(document, 'wikipedia_clicks', '0')
        self.add_field(document, 'derived_score', '0')

    def build_legacy_doc(self, document, entity_rows):
        for key, value in entity_rows.items():
            if(key == 'about'):
                hitcounts = self.ag_rc.get_term_count(value)
                wpedia_clicks = hitcounts["wpedia_clicks"] if "wpedia_clicks" in hitcounts else -1
                eu_df = hitcounts["eu_df"] if "eu_df" in hitcounts else 0
                eu_df = eu_df if(eu_df != -1) else 0
                ds = abs(wpedia_clicks * eu_df)
                self.add_field(document, 'europeana_doc_count', str(eu_df))
                self.add_field(document, 'wikipedia_clicks', str(wpedia_clicks))
                self.add_field(document, 'derived_score', str(ds))
            if(key != 'prefLabel' and key != 'altLabel'): continue
            field_name = "skos_" + key
            t = type(value)
            if(t is str):
                self.add_field(document, field_name, value)
            elif(t is list):
                [self.add_field(document, field_name, i) for i in value]
            elif(t is dict):
                for subkey, subvalue in value.items():
                    qualified_field_name = field_name + "." + subkey if (subkey != "def") else field_name
                    for sv in subvalue:
                        self.add_field(document, qualified_field_name, sv)
