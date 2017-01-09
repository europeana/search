import xml.etree.ElementTree as ET
import os, re

class PreviewBuilder:

    tree = ET.parse(os.path.join(os.path.dirname(__file__), 'professions.rdf'))

    PROFESSIONS = tree.getroot()
    ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'skos':'http://www.w3.org/2004/02/skos/core#', 'xml':'http://www.w3.org/XML/1998/namespace'}

    def __init__(self):
        from pymongo import MongoClient
        # note fixed import path
        from entities.ContextClassHarvesters import ContextClassHarvester
        import sys, os
        import yaml
        self.mongoclient = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        with open(os.path.join(os.path.dirname(__file__), 'fieldconfig.yml')) as yml:
            self.field_config = yaml.load(yml)

    def build_preview(self, entity_type, entity_id, entity_rows, language):
        import json
        fields_to_build = self.field_config[entity_type]
        preview_fields = {}
        preview_fields['id'] = entity_id
        preview_fields['type'] = entity_type
        for field in fields_to_build:
            val = getattr(self, 'build_' + field)(entity_rows, language, preview_fields)
            preview_fields['max_recall'] = self.build_max_recall(preview_fields['prefLabel'])
        return json.dumps(preview_fields)

    def build_max_recall(self, term):
        all_terms = [term]
        if(',' in term):
            term_bits = term.strip().split(',')
            term_bits.reverse()
            reversed_term = " ".join(term_bits)
        else:
            term_bits = term.strip().split()
            term_bits.insert(0, term_bits.pop())
            term_bits[0] = term_bits[0] + ","
            reversed_term = " ".join(term_bits)
        reversed_term = re.sub("\s+", " ", reversed_term.strip())
        all_terms.append(reversed_term)
        return all_terms

    def build_prefLabel(self, entity_rows, language, preview_fields):
        lang_key = 'def' if language not in entity_rows['representation']['prefLabel'] else language
        if lang_key in entity_rows['representation']['prefLabel']:
            preview_fields['prefLabel'] = entity_rows['representation']['prefLabel'][lang_key][0]

    def build_lifespan(self, entity_rows, language, preview_fields):
        # TODO: Validation routines to ensure agents have only one birthdate and deathdate apiece
        if('rdaGr2DateOfBirth' in entity_rows['representation'].keys()):
            lang_key = 'def' if language not in entity_rows['representation']['rdaGr2DateOfBirth'] else language
            if lang_key in entity_rows['representation']['rdaGr2DateOfBirth']:
                preview_fields['dateOfBirth'] = entity_rows['representation']['rdaGr2DateOfBirth'][lang_key][0]
        if('rdaGr2DateOfDeath' in entity_rows['representation'].keys()):
            lang_key = 'def' if language not in entity_rows['representation']['rdaGr2DateOfDeath'] else language
            if lang_key in entity_rows['representation']['rdaGr2DateOfDeath']:
                preview_fields['dateOfDeath'] = entity_rows['representation']['rdaGr2DateOfDeath'][lang_key][0]

    def build_role(self, entity_rows, language, preview_fields):
        if('rdaGr2ProfessionOrOccupation' in entity_rows['representation'].keys()):
            lang_key = 'def' if language not in entity_rows['representation']['rdaGr2ProfessionOrOccupation'] else language
            if lang_key in entity_rows['representation']['rdaGr2ProfessionOrOccupation']:
                roles = []
                for role in entity_rows['representation']['rdaGr2ProfessionOrOccupation'][lang_key]:
                    if role.startswith('http'):
                        test_role = PreviewBuilder.PROFESSIONS.find('./rdf:Description[@rdf:about="' + role + '"]/skos:prefLabel[@xml:lang="' + language + '"]', PreviewBuilder.ns)
                        if test_role is None:
                            test_role = role.split("/")[-1]
                        else:
                            test_role = test_role.text
                        roles.append(test_role)
                    else:
                        roles.append(role)
                preview_fields['professionOrOccupation'] = roles

    def build_country(self, entity_rows, language, preview_fields):
        if 'isPartOf' in entity_rows['representation'].keys():
            parents = []
            for lang_key in entity_rows['representation']['isPartOf']:
                for parent_uri in entity_rows['representation']['isPartOf'][lang_key]:
                    parent = self.mongoclient.annocultor_db.TermList.find_one({ 'codeUri' : parent_uri})
                    if(parent is not None):
                        pr_lang_key = lang_key if lang_key in parent['representation']['prefLabel'].keys() else ''
                        label = parent['representation']['prefLabel'][pr_lang_key][0]
                        pr_rep = { "id" : parent_uri, "prefLabel" : label }
                        parents.append(pr_rep)
            preview_fields['isPartOf'] = parents

    def build_topConcept(self, entity_rows, language):
        # TODO: update this method once top concepts dereferenceable
        concepts = {}
        concepts['def'] = 'Concept'
        return concepts


    def build_dateRange(self, entity_rows, language):
        pass
