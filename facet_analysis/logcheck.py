import xml.etree.ElementTree as ET
import os, re
from collections import namedtuple
from operator import attrgetter


# what we want to know
# how many fields need to be supported, given the kinds of queries our users
# are launching

# the wrinkle is that they are often querying against copyfields - that is to
# say, the question concerns the *underlying* fields, not the actual fields
# they are querying against

# desired output (for a variety of clients and query types)
# col 1: field queried against
# col 2: fields populating this field (if not identical)
# col 3: total number of queries

# step one: map copyfields to source fields
# if the field is not a copyfield, no sources are listed

# create a hash of fields to sources
field_defs = {}

tree = ET.parse('schema.xml')
root = tree.getroot()

copyfield_defs = {}

for copyfield in root.iter('copyField'):
    source = copyfield.attrib['source'].strip()
    dest = copyfield.attrib['dest'].strip()
    try:
        copyfield_defs[dest].append(source)
    except KeyError:
        copyfield_defs[dest] = [source]

for field in root[1].findall('./*[@name]'):
    if field.attrib['name'].strip() in copyfield_defs.keys():
        field_defs[field.attrib['name'].strip()] = copyfield_defs[field.attrib['name']]
    else:
        field_defs[field.attrib['name'].strip()] = []

# ok, let's filter out junk fields from our queries

"""with open('raw_source_data/all_fields_used.txt') as atu:
    with open('source_data/all_fields_used.txt', 'w') as atuout:
        for line in atu.readlines():
            (field, count) = line.split("\t")
            field = field.strip()
            count = count.strip()
            if(field in field_defs.keys()):
                msg = field + "\t" + str(count) + "\n"
                atuout.write(msg)

cwd = os.getcwd()
inpath = os.path.join(cwd, 'raw_source_data')
for f in os.listdir(inpath):
    if(not f.startswith("all")):
        with open(os.path.join(inpath,f)) as datafile:
            field_counts = {}
            for line in datafile.readlines():
                if(not line.startswith("K")):
                    (field, count) = line.split(":")
                    try:
                        field_counts[field.strip()] += int(count.strip())
                    except KeyError:
                        field_counts[field.strip()] = int(count.strip())
            outpath = os.path.join(cwd, 'source_data')
            newfile = "cleaned_" + f
            with open(os.path.join(outpath, newfile), 'w') as outdata:
                for k, v in field_counts.items():
                    msg = k + "\t" + str(v) + "\n"
                    outdata.write(msg) """

orig_fields_used = []
inpath = os.path.join(os.getcwd(), 'source_data')
outpath = os.path.join(os.getcwd(), 'fields_used')
Record = namedtuple('Record', 'fieldname base_fields count')
for f in os.listdir(inpath):
    records = []
    with open(os.path.join(inpath, f)) as datafile:
        with open(os.path.join(outpath, f), 'w') as outfile:
            for line in datafile.readlines():
                (field, count) = line.split("\t")
                field = field.strip()
                count = count.strip()
                if(field not in field_defs.keys() and re.match("\A.*\..{2}$", field)):
                    field = field[:-2] + "*"
                try:
                    if(len(field_defs[field]) > 0):
                        base_fields = ",".join(field_defs[field])
                    else:
                        base_fields = "---"
                    records.append(Record(field, base_fields, int(count)))
                except KeyError:
                    pass
            for r in sorted(records, key=attrgetter('count'), reverse=True):
                msg = r.fieldname + "\t" + r.base_fields + "\t" + str(r.count) + "\n"
                outfile.write(msg)
