import requests
import xml.etree.cElementTree as ET

# first we grab all the language codes

all_lang_codes = []

with open('langs_with_codes_sorted.txt', 'r') as langs:
    for lang in langs:
        langcode = lang.split('|')[1].strip()
        all_lang_codes.append(langcode)

# now we loop through them, retrieving the necessary docs from Solr
# and writing them to our output file
# note that we only need a couple of fields from each for testing purposes

solr = "http://sol1.eanadev.org:9191/solr/search_1/search?"
q = "*:*"
fl = "europeana_id,proxy_dc_title,proxy_dc_description"
rows = 50

for lang_code in all_lang_codes:
    codes = lang_code.split(',')
    codestring = " OR ".join(codes)
    codestring = "proxy_dc_language:(" + codestring + ")"
    solr_qry = solr + "wt=json&q=" + q + "&fl=" + fl + "&rows=" + str(rows) + "&fq=" + codestring
    print(solr_qry)
    qr = requests.get(solr_qry)
    root = ET.Element("add")
    for doc in qr.json()['response']['docs']:
        add_doc = ET.SubElement(root, 'doc')
        europeana_id=doc['europeana_id']
        ET.SubElement(add_doc, 'field', name="europeana_id").text = europeana_id
        try:
            for title in doc['proxy_dc_title']:
                ET.SubElement(add_doc, 'field', name="proxy_dc_title").text = title
            for desc in doc['proxy_dc_description']:
                ET.SubElement(add_doc, 'field', name="proxy_dc_description").text = desc
        except KeyError:
            pass
    tree = ET.ElementTree(root)
    filepath = "samples/"
    filename=lang_code + ".xml"
    fullpath = filepath + filename
    tree.write(fullpath, xml_declaration=True, encoding='utf-8')


