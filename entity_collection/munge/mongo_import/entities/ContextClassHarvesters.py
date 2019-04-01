import os, sys
from _sqlite3 import connect
class LanguageValidator:

    # TODO: What to do with weird 'def' language tags all over the place?
    LOG_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'logs', 'langlogs')

    def __init__(self):
        self.langmap = {}
        langlistloc = os.path.join(os.path.dirname(__file__), '..', 'all_langs.wkp')
        with open(langlistloc, 'r', encoding="UTF-8") as all_langs:
            for lang in all_langs:
                if(not(lang.startswith("#")) and ("|" in lang)):
                    (name, code) = lang.split('|')
                    self.langmap[code.strip()] = name

    def validate_lang_code(self, entity_id, code):
        if(code in self.langmap.keys()):
            return True
        elif(code == ContextClassHarvester.LANG_DEF):
            # TODO: sort out the 'def' mess at some point
            self.log_invalid_lang_code(entity_id, ContextClassHarvester.LANG_DEF)
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
        elif(code == ContextClassHarvester.LANG_DEF):
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

    DEFAULT_CONFIG_SECTION = 'CONFIG'
    HARVESTER_MONGO_HOST = 'harvester.mongo.host'
    HARVESTER_MONGO_PORT = 'harvester.mongo.port'
    
    ORGHARVESTER_MONGO_HOST = 'organization.harvester.mongo.host'
    ORGHARVESTER_MONGO_PORT = 'organization.harvester.mongo.port'
    
    CHUNK_SIZE = 250   # each file will consist of 250 entities
    WRITEDIR = os.path.join(os.path.dirname(__file__), '..', 'entities_out')
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
    LANG_VALIDATOR = LanguageValidator()
    LOG_LOCATION = 'logs/entlogs/'
    
    DC_IDENTIFIER = 'dc_identifier'
    ORGANIZATION_DOMAIN = 'organizationDomain'
    EUROPEANA_ROLE = 'europeanaRole'
    GEOGRAPHIC_LEVEL = 'geographicLevel'
    COUNTRY = 'country'
    
    REPRESENTATION = 'representation'
        
    LABEL = 'label'
    TYPE = 'type'
    TYPE_STRING = 'string'
    TYPE_REF = 'ref'
    LANG_DEF = 'def'
    LANG_EN = 'en'
    
    FIELD_MAP = {
        # maps mongo fields to their solr equivalents
        # TODO: there are numerous fields defined in the schema but not 
        # found in the actual data. They are accordingly not represented here.
        # For a list of all fields that might conceivably exist in accordance
        # with the data model, see https://docs.google.com/spreadsheets/d/
        #           1b1UN27M2eCia0L54di0KQY7KcndTq8-wxzwM4wN-8DU/edit#gid=340708208
        'prefLabel' : { LABEL : 'skos_prefLabel' , TYPE : TYPE_STRING },
        'altLabel' : { LABEL: 'skos_altLabel' , TYPE : TYPE_STRING },
        'hiddenLabel' : { LABEL : 'skos_hiddenLabel', TYPE : TYPE_STRING},
        'edmAcronym' : { LABEL : 'edm_acronym', TYPE : TYPE_STRING},
        'note' : { LABEL: 'skos_note' , TYPE : TYPE_STRING },
        'begin' : { LABEL : 'edm_begin', TYPE : TYPE_STRING},
        'end' : { LABEL : 'edm_end', TYPE : TYPE_STRING}, 
        'owlSameAs' : { LABEL: 'owl_sameAs' , TYPE : TYPE_REF },
        'edmIsRelatedTo' : { LABEL: 'edm_isRelatedTo' , TYPE : TYPE_REF },
        'dcIdentifier' : { LABEL: DC_IDENTIFIER , TYPE : TYPE_STRING },
        'dcDescription' : { LABEL: 'dc_description' , TYPE : TYPE_STRING },
        'rdaGr2DateOfBirth' : { LABEL: 'rdagr2_dateOfBirth' , TYPE : TYPE_STRING },
        #not used yet
        #'rdaGr2DateOfEstablishment' : { 'label': 'rdagr2_dateOfEstablishment' , TYPE : TYPE_STRING },
        'rdaGr2DateOfDeath' : { LABEL: 'rdagr2_dateOfDeath' , TYPE : TYPE_STRING },
        #not used yet
        #'rdaGr2DateOfTermination' : { 'label': 'rdagr2_dateOfTermination' , TYPE : TYPE_STRING },
        'rdaGr2PlaceOfBirth' : { LABEL: 'rdagr2_placeOfBirth' , TYPE : TYPE_STRING },
        'placeOfBirth' : { LABEL: 'rdagr2_placeOfBirth' , TYPE : TYPE_STRING },
        #not used yet
        #'placeOfBirth_uri' : { 'label': 'rdagr2_placeOfBirth.uri' , TYPE : TYPE_STRING },
        'rdaGr2PlaceOfDeath' : { LABEL: 'rdagr2_placeOfDeath' , TYPE : TYPE_STRING },
        #not used yet
        #'placeOfDeath_uri' : { 'label': 'rdagr2_placeOfDeath.uri' , TYPE : TYPE_STRING },
        'rdaGr2PlaceOfDeath' : { LABEL: 'rdagr2_placeOfDeath' , TYPE : TYPE_STRING },
        #not used yet
        #'professionOrOccupation_uri' : { 'label': 'professionOrOccupation.uri' , TYPE : TYPE_STRING },
        'rdaGr2ProfessionOrOccupation' :  { LABEL: 'rdagr2_professionOrOccupation' , TYPE : TYPE_STRING },
        #not used yet
        #'gender' : { 'label': 'gender' , TYPE : TYPE_STRING },
        'rdaGr2Gender' : { LABEL: 'rdagr2_gender' , TYPE : TYPE_STRING },
        'rdaGr2BiographicalInformation' : { LABEL: 'rdagr2_biographicalInformation' , TYPE : TYPE_STRING },
        'latitude' : { LABEL: 'wgs84_pos_lat' , TYPE : TYPE_STRING },
        'longitude' : { LABEL: 'wgs84_pos_long' , TYPE : TYPE_STRING },
        'begin' : { LABEL: 'edm_begin' , TYPE : TYPE_STRING },
        #not used yet
        #'beginDate' : { 'label': 'edm_beginDate' , TYPE : TYPE_STRING },
        'end' : { LABEL: 'edm_end' , TYPE : TYPE_STRING },
        #not used yet
        #'endDate' : { 'label': 'edm_endDate' , TYPE : TYPE_STRING },
        'isPartOf' : { LABEL: 'dcterms_isPartOf' , TYPE : TYPE_REF },
        'hasPart' : { LABEL : 'dcterms_hasPart', TYPE : TYPE_REF},
        'hasMet' : { LABEL : 'edm_hasMet', TYPE : TYPE_REF },
        'date' : { LABEL : 'dc_date', TYPE : TYPE_STRING },
        'exactMatch': { LABEL :  'skos_exactMatch', TYPE : TYPE_STRING },
        'related' : { LABEL : 'skos_related', TYPE : TYPE_REF  },
        'broader' : { LABEL : 'skos_broader', TYPE : TYPE_REF},
        'narrower' : { LABEL : 'skos_narrower', TYPE : TYPE_REF},
        'related' : { LABEL : 'skos_related', TYPE : TYPE_REF},
        'broadMatch' : { LABEL : 'skos_broadMatch', TYPE : TYPE_REF},
        'narrowMatch' : { LABEL : 'skos_narrowMatch', TYPE : TYPE_REF },
        'relatedMatch' : { LABEL : 'skos_relatedMatch', TYPE : TYPE_REF },
        'exactMatch' : { LABEL : 'skos_exactMatch', TYPE : TYPE_REF },
        'closeMatch' : { LABEL : 'skos_closeMatch', TYPE : TYPE_REF },
        'notation' : { LABEL : 'skos_notation', TYPE : TYPE_REF },
        'inScheme' : { LABEL : 'skos_inScheme', TYPE : TYPE_REF },
        'note' : { LABEL : 'skos_note', TYPE : TYPE_STRING },
        'foafLogo' : { LABEL : 'foaf_logo', TYPE : TYPE_REF },
        'foafDepiction' : { LABEL : 'foaf_depiction', TYPE : TYPE_REF },
        # not used yet
        #name' : { 'label' : 'foaf_name', TYPE : TYPE_STRING },
        'foafHomepage' : { LABEL : 'foaf_homepage', TYPE : TYPE_REF},
        'foafPhone' : { LABEL : 'foaf_phone', TYPE : TYPE_STRING},
        'foafMbox' : { LABEL : 'foaf_mbox', TYPE : TYPE_STRING},
        'edmCountry' : { LABEL : COUNTRY, TYPE : TYPE_STRING},
        'edmEuropeanaRole' : { LABEL : EUROPEANA_ROLE, TYPE : TYPE_STRING},
        'edmOrganizationDomain' : { LABEL : ORGANIZATION_DOMAIN, TYPE : TYPE_STRING},
        #TODO: remove, not supported anymore
        #'edmOrganizationSector' : { 'label' : 'edm_organizationSector', TYPE : TYPE_STRING},
        #'edmOrganizationScope' : { 'label' : 'edm_organizationScope', TYPE : TYPE_STRING},
        'edmGeographicLevel' : { LABEL : GEOGRAPHIC_LEVEL, TYPE : TYPE_STRING},
        'address_about' : { LABEL : 'vcard_hasAddress', TYPE : TYPE_STRING},
        'vcardStreetAddress' : { LABEL : 'vcard_streetAddress', TYPE : TYPE_STRING},
        'vcardLocality' : { LABEL : 'vcard_locality', TYPE : TYPE_STRING },
        #not used yet
        #'vcardRegion' : { LABEL : 'vcard_region', TYPE : TYPE_STRING },
        'vcardPostalCode' : { LABEL : 'vcard_postalCode', TYPE : TYPE_STRING},
        'vcardCountryName' : { LABEL : 'vcard_countryName', TYPE : TYPE_STRING },
        'vcardPostOfficeBox' : { LABEL : 'vcard_postOfficeBox', TYPE : TYPE_STRING},
        'vcardHasGeo' : { LABEL : 'vcard_hasGeo', TYPE : TYPE_STRING}
        
    }

    def log_warm_message(self, entity_id, message):
        # TODO: differentiate logfiles by date
        filename = "warn.txt"
        filepath = LanguageValidator.LOG_LOCATION + filename
        with open(filepath, 'a') as lgout:
            msg = "Warning info on processing entity " + str(entity_id) + ": " + str(message)
            lgout.write(msg)
            lgout.write("\n")

    # TODO: add address processing

    def __init__(self, name):
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'preview_builder'))
        
        from pymongo import MongoClient
        import PreviewBuilder
        import HarvesterConfig
        
        self.config = HarvesterConfig.HarvesterConfig()
        #TODO: check if entity_class is still needed
        #self.mongo_entity_class = entity_class
        self.name = name
        self.client = MongoClient(self.get_mongo_host(), self.get_mongo_port())
        self.ranking_model = self.config.get_relevance_ranking_model()
        self.write_dir = ContextClassHarvester.WRITEDIR + "/" + self.ranking_model
        #TODO create working dir here, including folders for individual entities and organization type
        entity_type = name[:-1]
        self.preview_builder = PreviewBuilder.PreviewBuilder(self.client, entity_type)
        
    def get_mongo_host (self):
        #return default mongo host, the subclasses may use the type based config (e.g. see organizations)
        return self.config.get_mongo_host() 
        
    def get_mongo_port (self):
        #return default mongo port, the subclasses may use the type based config (e.g. see also organizations host)
        return self.config.get_mongo_port()
    
    def extract_numeric_id(self, entity_id):
        parts = entity_id.split("/")
        #numeric id is the last part of the URL 
        return parts[len(parts) - 1]
    
    def build_solr_doc(self, entities, start, one_entity = False):
        from xml.etree import ElementTree as ET

        docroot = ET.Element('add')
        for entity_id, values  in entities.items():
            print("processing entity:" + entity_id)
            self.build_entity_doc(docroot, entity_id, values)
        self.client.close()
        return self.write_to_file(docroot, start, one_entity)
        

    def add_field_list(self, docroot, field_name, values):
        if(values is None):
            return
        for value in values:
            self.add_field(docroot, field_name, value)
        
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
        field_value = field_value.replace("\t", " ")
        return field_value

    def write_to_file(self, doc, start, one_entity):
        from xml.etree import ElementTree as ET
        from xml.dom import minidom
        import io
        writepath = self.get_writepath(start, one_entity)
        roughstring = ET.tostring(doc, encoding='utf-8')
        reparsed = minidom.parseString(roughstring)
        reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
        with io.open(writepath, 'w', encoding='utf-8') as writefile:
            writefile.write(reparsed)
            writefile.close()
        return writepath

    def get_writepath(self, start, one_entity):
        if(one_entity):
            return self.write_dir + "/individual_entities/"+ self.name + "/" + str(start) +  ".xml"
        else:
            return self.write_dir + "/" + self.name + "/" + self.name + "_" + str(start) + "_" + str(start + ContextClassHarvester.CHUNK_SIZE) +  ".xml"

    def grab_relevance_ratings(self, docroot, entity_id, entity_rows):
        hitcounts = self.relevance_counter.get_raw_relevance_metrics(entity_id, entity_rows)
        eu_enrichments = hitcounts["europeana_enrichment_hits"]
        eu_terms = hitcounts["europeana_string_hits"]
        pagerank = hitcounts["pagerank"]
        if(self.ranking_model == self.config.HARVESTER_RELEVANCE_RANKING_MODEL_DEFAULT):
            ds = self.relevance_counter.calculate_relevance_score(entity_id, pagerank, eu_enrichments, eu_terms)
        elif(self.ranking_model == self.config.HARVESTER_RELEVANCE_RANKING_MODEL_NORMALIZED):
            ds = self.relevance_counter.calculate_normalized_score(pagerank, eu_enrichments, eu_terms)
        else:
            raise ValueError("Must set property harvester.relevance.ranking.model to one of the values <default> or <normalized>")    
        self.add_field(docroot, 'europeana_doc_count', str(eu_enrichments))
        self.add_field(docroot, 'europeana_term_hits', str(eu_terms))
        self.add_field(docroot, 'pagerank', str(pagerank))
        self.add_field(docroot, 'derived_score', str(ds))
        self.add_suggest_filters(docroot, eu_terms)
        return True

    def process_address(self, docroot, entity_id, address):
        #TODO check if the full address is needed
        #address_components = []
        for k, v in address.items():
            key = k	
            value = v
            if ("about" == k):
                key = "address_" + k
            elif ("vcardHasGeo" == k):
                #remove geo:, keep just lat,long 
                value = v.split(":")[-1]
                    
            if(key not in ContextClassHarvester.FIELD_MAP.keys() & key != 'about'):
                self.log_warm_message(entity_id, "unmapped field: " + key)
                continue
        
            field_name = ContextClassHarvester.FIELD_MAP[key][self.LABEL]
            field_name = field_name + ".1"
            self.add_field(docroot, field_name, value)
            #address_components.append(v)

        #if(len(address_components) > 0):
        #    self.add_field(docroot, "vcard_fulladdresskey...", ",".join(address_components))

    def process_representation(self, docroot, entity_id, entity_rows):
        # TODO: Refactor to shrink this method
        import json
        #all pref labels
        all_preflabels = []
        for characteristic in entity_rows[self.REPRESENTATION]:
            if(characteristic == "address"):
                self.process_address(docroot, entity_id, entity_rows[self.REPRESENTATION]['address']['AddressImpl'])
            elif str(characteristic) not in ContextClassHarvester.FIELD_MAP.keys():
                # TODO: log this?
                print("unmapped property: " + str(characteristic))
                continue
            # TODO: Refactor horrible conditional
            elif(str(characteristic) == "dcIdentifier"):
                self.add_field_list(docroot, ContextClassHarvester.DC_IDENTIFIER, entity_rows[self.REPRESENTATION]['dcIdentifier'][self.LANG_DEF])
            elif(str(characteristic) == "edmOrganizationDomain"):
                #TODO: create method to add solr field for .en fields
                self.add_field(docroot, ContextClassHarvester.ORGANIZATION_DOMAIN + "." + self.LANG_EN, entity_rows[self.REPRESENTATION]['edmOrganizationDomain'][self.LANG_EN])
            elif(str(characteristic) == "edmEuropeanaRole"): 
                #multivalued
                roles = entity_rows[self.REPRESENTATION]['edmEuropeanaRole'][self.LANG_EN]
                self.add_field_list(docroot, ContextClassHarvester.EUROPEANA_ROLE + "." + self.LANG_EN, roles)
            elif(str(characteristic) == "edmGeographicLevel"):
                self.add_field(docroot, ContextClassHarvester.GEOGRAPHIC_LEVEL + "." + self.LANG_EN, entity_rows[self.REPRESENTATION]['edmGeographicLevel'][self.LANG_EN])
            elif(str(characteristic) == "edmCountry"):
                self.add_field(docroot, ContextClassHarvester.COUNTRY, entity_rows[self.REPRESENTATION]['edmCountry'][self.LANG_EN])
            #not supported anymore 
            #elif(str(characteristic) == "edmOrganizationSector"):
            #    self.add_field(docroot, "edm_organizationSector.en", entity_rows[self.REPRESENTATION]['edmOrganizationSector'][self.LANG_EN])
            #elif(str(characteristic) == "edmOrganizationScope"):
            #    self.add_field(docroot, "edm_organizationScope.en", entity_rows[self.REPRESENTATION]['edmOrganizationScope'][self.LANG_EN])            
            # if the entry is a dictionary (language map), then the keys should be language codes
            elif(type(entity_rows[self.REPRESENTATION][characteristic]) is dict):
                #for each entry in the language map
                for lang in entity_rows[self.REPRESENTATION][characteristic]:
                    pref_label_count = 0
                    #avoid duplicates when adding values from prefLabel
                    prev_alts = []
                    if(ContextClassHarvester.LANG_VALIDATOR.validate_lang_code(entity_id, lang)):
                        field_name = ContextClassHarvester.FIELD_MAP[characteristic][self.LABEL]
                        field_values = entity_rows[self.REPRESENTATION][characteristic][lang]
                        #property is language map of strings
                        if(type(field_values) == str):
                            unq_name = lang if lang != self.LANG_DEF else ''
                            q_field_name = field_name + "."+ unq_name
                            #field value = field_values
                            self.add_field(docroot, q_field_name, field_values) 
                        else:
                            #for each value in the list
                            for field_value in field_values:
                                q_field_name = field_name
                                unq_name = lang if lang != self.LANG_DEF else ''
                                if(ContextClassHarvester.FIELD_MAP[characteristic][self.TYPE] == self.TYPE_STRING):
                                    q_field_name = field_name + "."+ unq_name
                                # Code snarl: we often have more than one prefLabel per language in the data
                                # We can also have altLabels
                                # We want to shunt all but the first-encountered prefLabel into the altLabel field
                                # while ensuring the altLabels are individually unique
                                # TODO: Refactor (though note that this is a non-trivial refactoring)
                                # NOTE: prev_alts are for one language, all_preflabels include labels in any language
                                if(characteristic == 'prefLabel' and pref_label_count > 0):
                                    #move all additional labels to alt label
                                    q_field_name = "skos_altLabel." + unq_name
                                    #SG - TODO: add dropped pref labels to prev_alts??
                                    #prev_alts.append(field_value)
                                if('altLabel' in q_field_name):
                                    #TODO: SG why this? we skip alt labels here, but we don't add the gained entries from prefLabels
                                    
                                    if(field_value in prev_alts):
                                        continue
                                    prev_alts.append(field_value)
                                    #suggester uses alt labels for some entity types (organizations) 
                                    #disables until altLabels are added to payload 
                                    #self.add_alt_label_to_suggest(field_value, all_preflabels)
                                if(str(characteristic) == "edmAcronym"):
                                    #suggester uses alt labels for some entity types (organizations) 
                                    self.add_acronym_to_suggest(field_value, all_preflabels)
                                    
                                if(characteristic == 'prefLabel' and pref_label_count == 0):
                                    pref_label_count = 1
                                    #TODO: SG - the suggester could actually make use of all pref labels, but the hightlighter might crash
                                    all_preflabels.append(field_value)
                                
                                #add field to solr doc
                                self.add_field(docroot, q_field_name, field_value)                                                          
            #property is list
            elif(type(entity_rows[self.REPRESENTATION][characteristic]) is list):
                field_name = ContextClassHarvester.FIELD_MAP[characteristic][self.LABEL]
                for entry in entity_rows[self.REPRESENTATION][characteristic]:
                    self.add_field(docroot, field_name, entry)
            # property is a single value
            else: 
                try:
                    field_name = ContextClassHarvester.FIELD_MAP[characteristic][self.LABEL]
                    field_value = entity_rows[self.REPRESENTATION][characteristic]
                    self.add_field(docroot, field_name, str(field_value))
                except KeyError:
                    print('Attribute ' + field_name + ' found in source but undefined in schema.')
        #add suggester payload
        payload = self.build_payload(entity_id, entity_rows)
        self.add_field(docroot, 'payload', json.dumps(payload))
        #add suggester field
        all_preflabels = self.shingle_preflabels(all_preflabels)
        # SG: values in the same language are joined using space separator. values in different languages are joined using underscore as it is used as tokenization pattern. see schema.xml  
        self.add_field(docroot, 'skos_prefLabel', "_".join(sorted(set(all_preflabels))))
        depiction = self.preview_builder.get_depiction(entity_id)
        if(depiction):
            self.add_field(docroot, 'foaf_depiction', depiction)
        self.grab_relevance_ratings(docroot, entity_id, entity_rows[self.REPRESENTATION])

    def shingle_preflabels(self, preflabels):
        shingled_labels = []
        for label in preflabels:
            all_terms = label.split()
            for i in range(len(all_terms)):
                shingle = " ".join(all_terms[i:len(all_terms)])
                shingled_labels.append(shingle)
        return shingled_labels

    def build_payload(self, entity_id, entity_rows):
        #TODO set entity type as class attribute in Harvester
        entity_type = entity_rows['entityType'].replace('Impl', '')
        payload = self.preview_builder.build_preview(entity_type, entity_id, entity_rows[self.REPRESENTATION])
        return payload

    def add_suggest_filters(self, docroot, term_hits):
        entity_type = self.name[0:len(self.name) - 1].capitalize()
        self.add_field(docroot, 'suggest_filters', entity_type)
        if(term_hits > 0):
            self.add_field(docroot, 'suggest_filters', 'in_europeana')
    
    def suggest_by_alt_label(self):
        #this functionality can be activated by individual harvesters
        return False
    
    def suggest_by_acronym(self):
        #this functionality can be activated by individual harvesters
        return False
        
    def add_alt_label_to_suggest(self, value, suggester_values):
        if(self.suggest_by_alt_label() and (value not in suggester_values)):
            suggester_values.append(value)
            
    def add_acronym_to_suggest(self, value, suggester_values):
        if(self.suggest_by_acronym() and (value not in suggester_values)):
            suggester_values.append(value)
    
class ConceptHarvester(ContextClassHarvester):

    def __init__(self):
        # TODO check if 'eu.europeana.corelib.solr.entity.ConceptImpl' is correct and needed (see entityType column in the database)
        #ContextClassHarvester.__init__(self, 'concepts', 'eu.europeana.corelib.solr.entity.ConceptImpl')
        ContextClassHarvester.__init__(self, 'concepts')
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        from ranking_metrics import RelevanceCounter
        self.relevance_counter = RelevanceCounter.ConceptRelevanceCounter()

    def get_entity_count(self):
        #concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )
        concepts = self.client.annocultor_db.TermList.find({'entityType': 'ConceptImpl'}).count()
        return concepts

    def build_entity_chunk(self, start):
        #concepts = self.client.annocultor_db.concept.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/concept/base).*$' }} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        concepts = self.client.annocultor_db.TermList.distinct( 'codeUri', {'entityType': 'ConceptImpl'} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        concepts_chunk = {}
        for concept in concepts:
            concept_id = concept['codeUri']
            concepts_chunk[concept_id] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : concept_id })
        return concepts_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        uri = entity_rows['codeUri']
        self.add_field(doc, 'id', uri)
        self.add_field(doc, 'internal_type', 'Concept')
        self.process_representation(doc, uri, entity_rows)

class AgentHarvester(ContextClassHarvester):

    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        # TODO check if 'eu.europeana.corelib.solr.entity.AgentImpl' is correct and needed (see entityType column in the database)
        #ContextClassHarvester.__init__(self, 'agents', 'eu.europeana.corelib.solr.entity.AgentImpl')
        ContextClassHarvester.__init__(self, 'agents')
        self.relevance_counter = RelevanceCounter.AgentRelevanceCounter()

    def get_entity_count(self):
        #agents = self.client.annocultor_db.people.distinct( 'codeUri' )
        # TODO: refactor to generic implementation
        agents = self.client.annocultor_db.TermList.find({'entityType': 'AgentImpl'}).count()
        return agents

    def build_entity_chunk(self, start):
        #agents = self.client.annocultor_db.people.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        # TODO: refactor to generic implementation
        agents = self.client.annocultor_db.TermList.distinct( 'codeUri', {'entityType': 'AgentImpl'} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        
        agents_chunk = {}
        for agent in agents:
            agent_id = agent['codeUri']
            agents_chunk[agent_id] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : agent_id })
        return agents_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        if(entity_rows is None):
            self.log_missing_entry(entity_id)
            return
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', entity_id)
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
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        #TODO: check if 'eu.europeana.corelib.solr.entity.PlaceImpl' still needed/used
        #ContextClassHarvester.__init__(self, 'places', 'eu.europeana.corelib.solr.entity.PlaceImpl')
        ContextClassHarvester.__init__(self, 'places')
        self.relevance_counter = RelevanceCounter.PlaceRelevanceCounter()

    def get_entity_count(self):
        #place_list = self.client.annocultor_db.TermList.distinct( 'codeUri', { 'codeUri': {'$regex': '^(http://data\.europeana\.eu/place/).*$' }} )
        place_count = self.client.annocultor_db.TermList.find( {"entityType": "ConceptImpl"} ).count()
        return place_count

    def build_entity_chunk(self, start):
        #TODO rename variables, places-> entity
        #places = self.client.annocultor_db.place.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        places = self.client.annocultor_db.TermList.distinct( 'codeUri', {"entityType": "PlaceImpl"} )[start:start + ContextClassHarvester.CHUNK_SIZE]
        
        places_chunk = {}
        for place in places:
            place_id = place['codeUri']
            places_chunk[place] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : place_id })
        return places_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', entity_id)
        self.add_field(doc, 'internal_type', 'Place')
        self.process_representation(doc, entity_id, entity_rows)

class OrganizationHarvester(ContextClassHarvester):

    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ranking_metrics'))
        import RelevanceCounter
        #TODO: check if 'eu.europeana.corelib.solr.entity.OrganizationImpl' still needed/used
        #ContextClassHarvester.__init__(self, 'organizations', 'eu.europeana.corelib.solr.entity.OrganizationImpl')
        ContextClassHarvester.__init__(self, 'organizations')
        self.relevance_counter = RelevanceCounter.OrganizationRelevanceCounter()

    def get_mongo_host (self):
        return self.config.get_mongo_host(self.name)
     
    def suggest_by_alt_label(self):
        return True
    
    def suggest_by_acronym(self):
        return True
    
    def get_entity_count(self):
        org_count = self.client.annocultor_db.TermList.find( {'entityType': 'OrganizationImpl'} ).count()
        print("importing organizations: " + str(org_count))
        return org_count

    def build_entity_chunk(self, start):
        #orgs = self.client.annocultor_db.organization.distinct('codeUri')[start:start + ContextClassHarvester.CHUNK_SIZE]
        orgs = self.client.annocultor_db.TermList.find( {'entityType': 'OrganizationImpl'}, {'codeUri':1, '_id': 0})[start:start + ContextClassHarvester.CHUNK_SIZE]
        orgs_chunk = {}
        for org in orgs:
            org_id = org['codeUri']
            orgs_chunk[org_id] = self.client.annocultor_db.TermList.find_one({ 'codeUri' : org_id })
        return orgs_chunk

    def build_entity_doc(self, docroot, entity_id, entity_rows):
        sys.path.append('ranking_metrics')
        from xml.etree import ElementTree as ET
        doc = ET.SubElement(docroot, 'doc')
        self.add_field(doc, 'id', entity_id)
        self.add_field(doc, 'internal_type', 'Organization')
        self.process_representation(doc, entity_id, entity_rows)


class IndividualEntityBuilder:
    
    OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'tests', 'testfiles', 'dynamic')

    def build_individual_entity(self, entity_id):
        from pymongo import MongoClient
        import shutil
        if(entity_id.find("/place/") > 0):
            harvester = PlaceHarvester()
        elif(entity_id.find("/agent/") > 0):
            harvester = AgentHarvester()
        elif(entity_id.find("/organization/") > 0):
            harvester = OrganizationHarvester()
        else:
            harvester = ConceptHarvester()
        
        self.client = MongoClient(harvester.get_mongo_host(), harvester.get_mongo_port())
        entity_rows = self.client.annocultor_db.TermList.find_one({ "codeUri" : entity_id })
        entity_chunk = {}
        entity_chunk[entity_id] = entity_rows
        #rawtype = entity_rows['entityType']
        
        start = int(entity_id.split("/")[-1])
        #one_entity
        solrDocFile = harvester.build_solr_doc(entity_chunk, start, True)
        return solrDocFile
    
        #solrDocFile = rawtype[0:-4].lower() + "_" + str(start) + ".xml file."
        #if(not(is_test)): print("Entity " + entity_id + " written to " + solrDocFile)
        #if(is_test):
        #    current_location = harvester.get_writepath(start)
        #    namebits = entity_id.split("/")
        #    newname = namebits[-3] + "_" + namebits[-1] + ".xml"
        #    solrDocFile = IndividualEntityBuilder.OUTDIR + "/" + newname
        #    shutil.copyfile(current_location, solrDocFile)
        #    os.remove(current_location) # cleaning up
        #    return solrDocFile
#        except Exception as e:
#            print("No entity with that ID found in database. " + str(e))
#            return

class ChunkBuilder:

    def __init__(self, entity_type, start):
        self.entity_type = entity_type.lower()
        self.start = start

    def build_chunk(self):
        #TODO 
        if(self.entity_type == "concept"):
            harvester = ConceptHarvester()
        elif(self.entity_type == "agent"):
            harvester = AgentHarvester()
        elif(self.entity_type == "place"):
            harvester = PlaceHarvester()
        elif(self.entity_type == "organization"):
            harvester = OrganizationHarvester()
        ec = harvester.build_entity_chunk(self.start)
        harvester.build_solr_doc(ec, self.start)
