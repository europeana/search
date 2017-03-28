import xml.etree.ElementTree as ET
from collections import namedtuple

tree = ET.parse('schema.xml')
root = tree.getroot()

# let's just build a set of all copyfield targets and all
# string datatype fields, and then take the intersection
field_configs = []
field_config = namedtuple('FieldConfig', 'field_name source_fields source_types')

cfs = [copyfield.attrib['dest'] for copyfield in root.iter('copyField')]
cfs = set(cfs)

fs = [field.attrib['name'] for field in root[1].iter('field') if field.attrib['type'] == 'string']
fs = set(fs)

potential_facet_fields = set.intersection(cfs, fs)

for pff in potential_facet_fields:
    sources = [copyfield.attrib['source'] for copyfield in root.iter('copyField') if copyfield.attrib['dest'] == pff]
    types = [field.attrib['type'] for field in root[1].findall('./*[@name]') for source in sources if field.attrib['name'] == source]
    field_configs.append(field_config(pff, sources, types))

with open('facet_field_defs.txt', 'w') as ffd:
    for fc in sorted(field_configs):
        msg = fc.field_name + "\t" + ",".join(fc.source_fields) + "\t" + ",".join(fc.source_types) + "\n"
        ffd.write(msg)
