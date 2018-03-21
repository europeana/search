import xml.etree.ElementTree as ET
import os, re

class PreviewBuilder:

    jobtree = ET.parse(os.path.join(os.path.dirname(__file__), 'professions.rdf'))
    PROFESSIONS = jobtree.getroot()
    ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'skos':'http://www.w3.org/2004/02/skos/core#', 'xml':'http://www.w3.org/XML/1998/namespace'}

    def __init__(self):
        from pymongo import MongoClient
        # note fixed import path
        from entities.ContextClassHarvesters import ContextClassHarvester
        import sys, os
        import yaml
        self.load_depictions()
        self.mongoclient = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)

    def build_preview(self, entity_type, entity_id, entity_rows):
        import json
        preview_fields = {}
        preview_fields['id'] = entity_id
        preview_fields['type'] = entity_type
        preview_fields['prefLabel'] = self.build_pref_label(entity_rows)
        preview_fields['hiddenLabel'] = self.build_max_recall(entity_type, entity_rows)
        if(self.get_depiction(entity_id)):
            preview_fields['depiction'] = self.get_depiction(entity_id)
        if(entity_type == "Agent"):
            if(self.build_birthdate(entity_rows)): preview_fields['dateOfBirth'] = self.build_birthdate(entity_rows)
            if(self.build_deathdate(entity_rows)): preview_fields['dateOfDeath'] = self.build_deathdate(entity_rows)
            if(self.build_role(entity_rows)): preview_fields['professionOrOccupation'] = self.build_role(entity_rows)
        elif(entity_type == "Place"):
            if(self.build_country_label(entity_rows)): preview_fields['isPartOf'] = self.build_country_label(entity_rows)
        return preview_fields

    def build_pref_label(self, entity_rows):
        all_langs = {}
        for k in entity_rows['prefLabel']:
            all_langs[k] = entity_rows['prefLabel'][k][0]
        return all_langs

    def build_max_recall(self, entity_type, entity_rows):
        all_langs = {}
        for k in entity_rows['prefLabel']:
            all_langs[k] = self.transpose_terms(entity_type, entity_rows['prefLabel'][k][0])
        return all_langs

    def transpose_terms(self, type, term):
        # reimplements (with trim_term())
        # https://github.com/europeana/uim-europeana/blob/master/workflow_plugins/
        # europeana-uim-plugin-enrichment/src/main/java/eu/europeana/uim/enrichment/
        # normalizer/AgentNormalizer.java
        term = self.trim_term(term)
        all_terms = [term]
        if(type != 'Agent'): # only agents need bibliographic inversion
            return all_terms
        elif(' ' not in term): # not possible to invert a single term
            return all_terms
        elif(',' in term):
            term_bits = term.strip().split(',')
            term_bits.reverse()
            reversed_term = " ".join(term_bits)
        else:
            term_bits = term.split()
            term_bits.insert(0, term_bits.pop())
            term_bits[0] = term_bits[0] + ","
            reversed_term = " ".join(term_bits)
        reversed_term = re.sub("\s+", " ", reversed_term.strip())
        all_terms.append(reversed_term)
        return all_terms

    def trim_term(self, term):
        term = term.strip()
        if("(" in term):
            term = term.split("(")[0]
        elif("[" in term):
            term = term.split("[")[0]
        elif("<" in term):
            term = term.split("<")[0]
        elif(";" in term):
            term = term.split(";")[0]
        return term

    def build_birthdate(self, entity_rows):
        # TODO: Validation routines to ensure agents have only one birthdate and deathdate apiece
        if('rdaGr2DateOfBirth' in entity_rows.keys()):
            for lang in entity_rows['rdaGr2DateOfBirth'].keys():
                dob = entity_rows['rdaGr2DateOfBirth'][lang][0]
                break
            return dob
        else:
            return None

    def build_deathdate(self, entity_rows):
        if('rdaGr2DateOfDeath' in entity_rows.keys()):
            for lang in entity_rows['rdaGr2DateOfDeath'].keys():
                dod = entity_rows['rdaGr2DateOfDeath'][lang][0]
                break
            return dod
        else:
            return None

    def build_role(self, entity_rows):
        roles = {}
        uris = []
        if('rdaGr2ProfessionOrOccupation' in entity_rows.keys()):
            for language in entity_rows['rdaGr2ProfessionOrOccupation']:
                for role in entity_rows['rdaGr2ProfessionOrOccupation'][language]:
                    if role.startswith('http'):
                        uris.append(role)
                    else:
                        try:
                            roles[language].append(role)
                        except KeyError:
                            roles[language] = [role]
            for uri in uris:
                role = PreviewBuilder.PROFESSIONS.find('./rdf:Description[@rdf:about="' + uri + '"]', PreviewBuilder.ns)
                if(role):
                    for role_label in role.findall("skos:prefLabel"):
                        label_contents = role_label.text
                        language = role_label.attrib["xml:lang"]
                        try:
                            roles[language].append(label_contents)
                        except KeyError:
                            roles[language] = [label_contents]
            return roles
        else:
            return None

    def build_country_label(self, entity_rows):
        if 'isPartOf' in entity_rows.keys():
            parents = set([parent_uri for k in entity_rows['isPartOf'].keys() for parent_uri in entity_rows['isPartOf'][k]])
            upper_geos = {}
            for parent_uri in parents:
                parent = self.mongoclient.annocultor_db.TermList.find_one({ 'codeUri' : parent_uri})
                if(parent is not None):
                    upper_geos[parent_uri] = {}
                    for lang in parent['representation']['prefLabel']:
                        label = parent['representation']['prefLabel'][lang][0]
                        upper_geos[parent_uri][lang] = label
            if(len(upper_geos.keys()) > 0): return upper_geos
            return None

    def build_topConcept(self, entity_rows, language):
        # TODO: update this method once top concepts dereferenceable
        concepts = {}
        concepts['def'] = 'Concept'
        return concepts


    def build_dateRange(self, entity_rows, language):
        pass

    # temporary (?!) hack - right now Agents are the only entity type with images
    # and they are pulled in ad hoc from a static file

    def load_depictions(self):
        self.depictions = {}
        image_files = ['agents.wikidata.images.csv', 'concepts.merge.images.csv']
        for image_file in image_files:
            with open(os.path.join(os.getcwd(), 'entities', 'resources', image_file)) as imgs:
                for line in imgs.readlines():
                    (agent_id, image_id) = line.split(sep=",", maxsplit=1)
                    agent_id = agent_id.strip()
                    image_id = image_id.strip()
                    self.depictions[agent_id] = image_id


    def get_depiction(self, entity_key):
        entity_key = entity_key.strip()
        try:
            raw_loc = self.depictions[entity_key]
            loc = re.sub(r"^\"", "", raw_loc)
            loc = re.sub(r"\"$", "", loc)
            print(loc)
            return loc
        except KeyError:
            None
