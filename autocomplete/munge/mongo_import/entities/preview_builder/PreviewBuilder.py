class PreviewBuilder:

    CLASS_TO_URI_MAP = {

        'Agent': 'http://www.europeana.eu/schemas/edm/Agent',
        'Concept' : 'https://www.w3.org/2009/08/skos-reference/skos.html#Concept',
        'Place' : 'http://www.europeana.eu/schemas/edm/Place'

    }

    def __init__(self):
        from pymongo import MongoClient
        from ContextClassHarvesters import ContextClassHarvester
        import yaml
        self.lv = ContextClassHarvester.LANG_VALIDATOR
        self.mongoclient = MongoClient(ContextClassHarvester.MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        self.legacymongo = MongoClient(ContextClassHarvester.LEGACY_MONGO_HOST, ContextClassHarvester.MONGO_PORT)
        with open('preview_builder/fieldconfig.yml') as yml:
            self.field_config = yaml.load(yml)

    def build_preview(self, entity_type, entity_id, entity_rows):
        import json
        fields_to_build = self.field_config[entity_type]
        retfields = {}
        retfields['type'] = self.CLASS_TO_URI_MAP[entity_type]
        for field in fields_to_build:
            val = getattr(self, 'build_' + field)(entity_rows)
            retfields[field] = val
        multilingual_labels = self.line_up_languages(retfields)
        multilingual_labels['entity_id'] = entity_id
        return json.dumps(multilingual_labels)

    def build_prefLabel(self, entity_rows):
        labels = {}
        for lang in entity_rows['representation']['prefLabel']:
            if(self.lv.pure_validate_lang_code(lang)):
                labels[lang] = entity_rows['representation']['prefLabel'][lang]
        return labels

    def build_lifespan(self, entity_rows):
        # TODO: Validation routines to ensure agents have only one birthdate and deathdate apiece
        birthdates = {}
        deathdates = {}
        if('rdaGr2DateOfBirth' in entity_rows['representation'].keys()):
            for lang in entity_rows['representation']['rdaGr2DateOfBirth']:
                birthdates[lang] = entity_rows['representation']['rdaGr2DateOfBirth'][lang][0]
        if('rdaGr2DateOfDeath' in entity_rows['representation'].keys()):
            for lang in entity_rows['representation']['rdaGr2DateOfDeath']:
                deathdates[lang] = entity_rows['representation']['rdaGr2DateOfDeath'][lang][0]
        births_w_deaths = []
        births_wo_deaths = []
        deaths_wo_births = []
        for k in birthdates.keys():
            if k in deathdates.keys() or 'def' in deathdates.keys(): births_w_deaths.append(k)
            else: births_wo_deaths.append(k)
        for k in deathdates.keys():
            if k not in birthdates.keys() and 'def' not in birthdates.keys():deaths_wo_births.append(k)
        all_dates = {}
        for lang in births_w_deaths:
            birthdate = birthdates[lang]
            deathdate = deathdates[lang] if lang in deathdates.keys() else deathdates['def']
            all_dates[lang] = birthdate + "-" + deathdate
        for lang in births_wo_deaths:
            birthdate = birthdates[lang]
            all_dates[lang] = birthdate + "-"
        for lang in deaths_wo_births:
            deathdate = deathdates[lang]
            all_dates[lang] = "? -" + deathdate
        return all_dates

    def build_role(self, entity_rows):
        roles = {}
        if('rdaGr2ProfessionOrOccupation' in entity_rows['representation'].keys()):
            for lang in entity_rows['representation']['rdaGr2ProfessionOrOccupation']:
                roles[lang] = entity_rows['representation']['rdaGr2ProfessionOrOccupation'][lang]
        return roles

    def build_country(self, entity_rows):
        country = {}
        if 'parent' in entity_rows.keys():
            next_level_up = entity_rows['parent']
            nlu_chunk = self.mongoclient.annocultor_db.TermList.find_one({'codeUri': next_level_up })
            for lang in nlu_chunk['representation']['prefLabel']:
                    country[lang] = nlu_chunk['representation']['prefLabel'][lang]
        return country

    def build_topConcept(self, entity_rows):
        concepts = {}
        # if 'broader' in entity_rows.keys():
        #    category_uri = entity_rows['broader']
        #    print(category_uri)
        #    top_concept = self.legacymongo.Concept.find_one({'about' : category_uri })
        #    for lang in top_concept['prefLabel'].keys():
        #        label = top_concept['prefLabel'][lang][0]
        #         concepts[lang] = label
        concepts['def'] = 'Concept'
        return concepts


    def build_dateRange(self, entity_rows):
        pass

    def line_up_languages(self, langmap):
        all_langs = {}
        pref_labels = langmap['prefLabel']
        for lang in pref_labels:
            if(len(lang) == 0): continue
            all_langs[lang] = {}
            all_langs[lang]['prefLabel'] = pref_labels[lang]
            all_langs[lang]['type'] = langmap['type']
            for key in langmap:
                if key == 'prefLabel': continue
                if key == 'type': continue
                else:
                    if langmap[key] is None:
                        all_langs[lang][key] = None
                    elif lang in langmap[key]:
                        try:
                            # print("Lang is " + lang + " and key is " + key)
                            all_langs[lang][key] = langmap[key][lang]
                        except TypeError as te:
                            print("ERROR!:"+ langmap)
                    elif 'def' in langmap[key]:
                        all_langs[lang][key] = langmap[key]['def']
        return all_langs
