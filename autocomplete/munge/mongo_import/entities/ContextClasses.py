class ContextualClass:

    from pymongo import MongoClient

    MONGO_HOST = 'mongodb://mongo2.eanadev.org'
    MONGO_PORT = 27017
    CLIENT = MongoClient(MONGO_HOST, MONGO_PORT)
    CHUNK_SIZE = 100
    WRITEDIR = 'entities_out'

    def __init__(self, name, entity_class):
        self.mongo_entity_class = entity_class
        self.name = name

    def loop_through_entities(self):
        start = 0
        concepts = ContextualClass.CLIENT.europeana.Concept
        # concept_count = concepts.find({'className': 'eu.europeana.corelib.solr.entity.ConceptImpl'}).count()
        concept_count = 200
        while(start < concept_count):
            concepts_chunk = concepts.find({'className': self.mongo_entity_class })[start:(start + ContextualClass.CHUNK_SIZE)]
            self.build_solr_doc(concepts_chunk, start)
            start += ContextualClass.CHUNK_SIZE

    def build_solr_doc(self, entity_list, start):
        from xml.etree import ElementTree as ET

        docroot = ET.Element('add')
        for entity in entity_list:
            self.build_entity_doc(docroot, entity)
        self.write_to_file(docroot, start)

    def add_field(self, docroot, field_name, field_value):
        from xml.etree import ElementTree as ET

        f = ET.SubElement(docroot, 'field')
        f.set('name', field_name)
        f.text = field_value

    def write_to_file(self, doc, start):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        writepath = "../" + ContextualClass.WRITEDIR + "/" + self.name + "/" + self.name + "_" + str(start) + "_" + str(start + ContextualClass.CHUNK_SIZE) +  ".xml"
        roughstring = ET.tostring(doc, 'utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed.writexml( open(writepath, 'w'), indent="    ", addindent="    ", newl="\n")
        reparsed.unlink()
        print("Complete") # TODO: change to Celery output

class Concept(ContextualClass):

    def __init__(self):
        ContextualClass.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')

    def build_entity_doc(self, docroot, entity_rows):
        from xml.etree import ElementTree as ET

        doc = ET.SubElement(docroot, 'doc')
        id = entity_rows['about']
        xid = ET.SubElement(doc, 'field')
        xid.set("name", "europeana_id")
        xid.text = id
        for key, value in entity_rows.items():
            if(key == 'about'): continue
            field_name = "skos_" + key
            t = type(value)
            if(t is str):
                self.add_field(doc, field_name, value)
            elif(t is list):
                [self.add_field(doc, field_name, i) for i in value]
            elif(t is dict):
                for subkey, subvalue in value.items():
                    qualified_field_name = field_name + "." + subkey
                    for sv in subvalue:
                        self.add_field(doc, qualified_field_name, sv)

c = Concept()
c.loop_through_entities()



