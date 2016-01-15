class ContextClassHarvester:

    from os import getcwd

    MONGO_HOST = 'mongodb://mongo1.eanadev.org'
    MONGO_PORT = 27017
    CHUNK_SIZE = 1000
    WRITEDIR = getcwd() + '/../entities_out'
    JAVA_TO_FRIENDLY_MAP = {
        # mongo stores the Java class names for each entity type
        # we want to translate these to more human-readable values
        'eu.europeana.corelib.solr.entity.ConceptImpl' : 'Concept',
        # TODO: Add remaining classes here
    }

    def __init__(self, name, entity_class):
        from pymongo import MongoClient

        self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)

    def build_solr_doc(self, entities, start):
        from xml.etree import ElementTree as ET

        docroot = ET.Element('add')
        for entity in entities:
            self.build_entity_doc(docroot, entity)
        self.client.close()
        return self.write_to_file(docroot, start)

    def add_field(self, docroot, field_name, field_value):
        from xml.etree import ElementTree as ET

        f = ET.SubElement(docroot, 'field')
        f.set('name', field_name)
        f.text = field_value

    def write_to_file(self, doc, start):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        writepath = ContextClassHarvester.WRITEDIR + "/" + self.name + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"
        roughstring = ET.tostring(doc, 'utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8')
        with open(writepath, 'w') as writefile:
            writefile.write(reparsed)
            writefile.close()
        return writepath

class ConceptHarvester(ContextClassHarvester):

    def __init__(self):
        ContextClassHarvester.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')

    def get_entity_count(self):
        concepts = self.client.europeana.Concept
        concepts_count = concepts.find({ 'className' : self.mongo_entity_class}).count()
        return concepts_count

    def build_entity_chunk(self, start):
        concepts = self.client.europeana.Concept
        concepts_chunk = concepts.find({ 'className' : self.mongo_entity_class})[start:(start + ContextClassHarvester.CHUNK_SIZE)]
        return concepts_chunk

    def build_entity_doc(self, docroot, entity_rows):
        from xml.etree import ElementTree as ET

        doc = ET.SubElement(docroot, 'doc')
        id = entity_rows['about']
        self.add_field(doc, 'europeana_id', id)
        self.add_field(doc, 'class_name', self.mongo_entity_class)
        self.add_field(doc, 'class_name_short', ContextClassHarvester.JAVA_TO_FRIENDLY_MAP[self.mongo_entity_class])
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





