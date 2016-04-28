import requests
import xml.etree.cElementTree as ET

# restricting sample documents to Europeana core languages as identified
# by EuropeanaConnect: English, German, Spanish, French, Italian, Polish

# we retrieve by both country and language, on the assumption that this
# gives us the best guide to language of the metadata (as opposed to language of the item

lang2country = {'en':'united kingdom', 'de':'germany', 'es':'spain', 'fr':'france', 'it':'italy', 'pl':'poland'}


# now we loop through them, retrieving the necessary docs from Solr
# and writing them to our output file
# note that we only need a couple of fields from each for testing purposes

solr = "http://sol1.eanadev.org:9191/solr/search_1/search?"
q = "*:*"
fl = "europeana_id,proxy_dc_title,proxy_dc_description"
rows = 5
desired_docs=50

for langcode, country in lang2country.items():
    # first we get the count of all items
    filters = "COUNTRY:\"" + country + "\" proxy_dc_language:" + langcode
    count_qry = solr + "wt=json&q=*:*&rows=0&fq=" + filters
    qr = requests.get(count_qry).json()
    count = qr['response']['numFound']
    its_reqd = int(desired_docs / rows)
    page_size = 10000
    mindocs_reqd = (page_size * its_reqd) + rows
    max_count = mindocs_reqd
    skip = page_size
    if(count < mindocs_reqd):
        max_count = count - rows
        skip = int(max_count / its_reqd)
    for i in range(0, max_count, skip):
        doc_qry = solr + "wt=json&q=*:*&rows=" + str(rows) + "&start=" + str(i) + "&fq=" + filters + "&fl=" + fl
        dqr = requests.get(doc_qry)
        root = ET.Element("add")
        for doc in dqr.json()['response']['docs']:
            add_doc = ET.SubElement(root, 'doc')
            europeana_id=doc['europeana_id']
            ET.SubElement(add_doc, 'field', name="europeana_id").text = europeana_id
            ET.SubElement(add_doc, 'field', name="targetlang").text = langcode
            try:
                for title in doc['proxy_dc_title']:
                    ET.SubElement(add_doc, 'field', name="proxy_dc_title").text = title
                for desc in doc['proxy_dc_description']:
                    ET.SubElement(add_doc, 'field', name="proxy_dc_description").text = desc
            except KeyError:
                pass
        tree = ET.ElementTree(root)
        filepath = "samples/" + langcode + "/"
        filename = langcode + "_" + str(i) + ".xml"
        fullpath = filepath + filename
        tree.write(fullpath, xml_declaration=True, encoding='utf-8')




