import requests, json

langs = ['bg','ca','cs','da','de','el','en','es','et','eu','fi','fr','ga','gd','he','hr','hu','ie','is','it','ka','lt','lv','mk','mt','mul','nl','no','pl','pt','ro','ru','sk','sl','sr','sv','tr','uk','yi','cy','sq','hy','az','be','bs','gl','ja','ar','ko','zh','hi']
ents = ['Place', 'Concept', 'Agent']
in_euro = "&fq=(europeana_doc_count:[1 TO *] OR europeana_term_hits:[1 TO *])"
SOLR_URI = "http://entity-api.eanadev.org:9191/solr/production/select?wt=json&rows=0&q=*:*&fq=skos_prefLabel."

with open('counts', 'w') as counts:
    for lang in langs:
        print(lang)
        LANG_URI = SOLR_URI + lang + ":*"
        for ent in ents:
            ENT_URI = LANG_URI + "&fq=internal_type:" + ent
            try:
                cnt = requests.get(ENT_URI).json()['response']['numFound']
                FIL_ENT_URI = ENT_URI + in_euro
                filcnt = requests.get(FIL_ENT_URI).json()['response']['numFound']
                first_col = lang if ent == 'Place' else "\t"
                msg = first_col + "\t" + ent + "\t" + str(cnt) + "\t" + str(filcnt)
                print(msg)
                counts.write(msg)
            except Exception as e:
                print("Problem retrieving entity type " + ent + " and language " + lang + ".  " + str(e))
        try:
            total = requests.get(LANG_URI).json()['response']['numFound']
            FIL_LANG_URI = LANG_URI + in_euro
            fil_total = requests.get(FIL_LANG_URI).json()['response']['numFound']
            msg = "\t\tTotal\t" + str(total) + "\t" + str(fil_total)
            print(msg)
            counts.write(msg)
        except Exception as ex:
            print("Problem retrieving totals for language " + lang + ".  " + str(ex))
