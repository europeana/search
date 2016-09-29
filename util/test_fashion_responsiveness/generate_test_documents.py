# desired characteristics of test corput
# 1 000 000 documents
# 4 fields in two groups
# 1st group: 25 000 distinct values, avg 1.5 values per record
# 2nd group: 1 500 distinct values, avg. 3 values per record

# each of the two groups has a URL and a label
import random
from xml.etree import ElementTree as ET
from math import ceil
from xml.dom import minidom
import io


tree = ET.parse('../../fashion_faceting/fash_thesaurus.rdf.xml')
root = tree.getroot()
schemata = []
ns = {

    'skos' : 'http://www.w3.org/2004/02/skos/core#',
    'rdf' : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xml': 'http://www.w3.org/XML/1998/namespace'

}
raw_terms = {}
for description in root:
    schema = description.find('skos:inScheme', ns)
    if(schema is not None):
        schema_label = schema.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'].split("/")[-1]
        pref_label = description.find('skos:prefLabel[@xml:lang="en"]', ns).text
        uri_ref = description.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about']
        if(schema_label not in raw_terms.keys()):
            raw_terms[schema_label] = []
        raw_terms[schema_label].append(pref_label + "|"+ uri_ref)

terms = {}
for term in raw_terms.keys():
    vals = set(raw_terms[term])
    terms[term] = vals

subject_target = 25000
type_target = 1500
total_subjects = len(terms['Subject'])
total_types = len(terms['Type'])
subject_factor = ceil(subject_target / float(total_subjects)) - 1
types_factor = ceil(type_target / float(total_types)) - 1
lorems = []
with open('lorem_ipsum.txt', 'r') as l:
    for line in l:
        if(line.strip() not in lorems): lorems.append(line.strip())

subject_uris = []
subject_terms = []

def gibber(word, original_word, length_comp):
    lterm = list(word)
    rterm = random.sample(lterm, len(lterm))
    gibberish = "".join(rterm)
    length_comp = len(str(length_comp))
    new_length = len(original_word) + length_comp
    return gibberish[0:new_length].strip()

for uniq_term in terms['Subject']:
    (term,uri) = uniq_term.split("|")
    random_terms = random.sample(lorems, subject_factor)
    subject_uris.append(uri)
    subject_terms.append(term)
    for i in range(subject_factor):
        new_uri = uri + str(i)
        raw_term = term + " " + random_terms[i]
        new_term = gibber(raw_term, term, i)
        subject_uris.append(new_uri)
        subject_terms.append(new_term)

type_uris = []
type_terms = []

for uniq_term in terms['Type']:
    (term,uri) = uniq_term.split("|")
    random_terms = random.sample(lorems, types_factor)
    type_uris.append(uri)
    type_terms.append(term)
    for i in range(types_factor):
        new_uri = uri + str(i)
        raw_term = term + " " + random_terms[i]
        new_term = gibber(raw_term, term, i)
        type_uris.append(new_uri)
        type_terms.append(new_term)

docroot = ET.Element('add')

TARGET = 1000
PER_FILE = 100
WRITEPATH = "samples/sample_"

for i in range(TARGET + 1):
    if(i % PER_FILE == 0):
        if(i > 0):
            outfile = WRITEPATH + str(int(i / PER_FILE)) + ".xml"
            roughstring = ET.tostring(docroot, encoding='utf-8')
            reparsed = minidom.parseString(roughstring)
            reparsed = reparsed.toprettyxml(encoding='utf-8', indent="     ").decode('utf-8')
            with io.open(outfile, 'w', encoding='utf-8') as writefile:
                writefile.write(reparsed)
                writefile.close()
        docroot = None
        docroot = ET.Element('add')
    subject_index = i % subject_target
    type_index = i % type_target
    subject_uri = subject_uris[subject_index]
    subject_term = subject_terms[subject_index]
    type_uri = type_uris[type_index]
    type_term = type_terms[type_index]
    item_id = "item_" + str(i)
    collection = "a" if (i % 2 == 0) else "b"
    doc = ET.SubElement(docroot, "doc")
    xml_id = ET.SubElement(doc, "id")
    xml_id.text = item_id
    xml_collection = ET.SubElement(doc, "collection")
    xml_collection.text = collection
    xml_suri = ET.SubElement(doc, "subject_uri")
    xml_suri.text = subject_uri
    xml_sterm = ET.SubElement(doc, "subject_term")
    xml_sterm.text = subject_term
    xml_turi = ET.SubElement(doc, "type_uri")
    xml_turi.text = type_uri
    xml_tterm = ET.SubElement(doc, "type_term")
    xml_tterm.text = type_term
