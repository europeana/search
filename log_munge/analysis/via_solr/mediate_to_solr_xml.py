import xml.etree.ElementTree as ET
import os
import re
import sys


READ_DIR = '../../log_extractor/intermediate_output/entries_by_session'
WRITE_DIR = 'as_xml'

def parse_filters(raw_filters):
	# returns a dictionary where the keys are the field name
	# and the values are the values (typically a list of values)
	if(raw_filters == ""):
		return {}
	raw_filters = raw_filters.strip()
	filters = eval(raw_filters)
	new_filters = {}
	for k, v in filters.items():
		new_filters[k] = eval(str(v))
	return new_filters

def convert_to_xml(interaction_type, timestamp, session_id, search_term, filters, num_results, rank_position=-1, uri=None):
	root = ET.Element("doc")
	el_it = ET.SubElement(root, 'field')
	el_it.set("name", "operation")
	el_it.text = interaction_type
	el_timestamp = ET.SubElement(root, 'field')
	el_timestamp.set("name", "interaction_timestamp")
	el_timestamp.text = timestamp
	el_sessid = ET.SubElement(root, 'field')
	el_sessid.set("name", "session_id")
	el_sessid.text = session_id
	el_search_term = ET.SubElement(root, 'field')
	el_search_term.set("name", "search_term")
	el_search_term.text = search_term
	el_num_results = ET.SubElement(root, 'field')
	el_num_results.set("name", "total_results")
	el_num_results.text = str(num_results)
	if(int(rank_position) > -1):
		el_rank_position = ET.SubElement(root, 'field')
		el_rank_position.set("name", "rank_position")
		el_rank_position.text = str(rank_position)
	if(uri is not None):
		el_uri = ET.SubElement(root, 'field')
		el_uri.set("name", "uri")
		uri = "http://www.europeana.eu/portal/en/record" + uri
		el_uri.text = uri
	for k, v in filters.items():
		if(type(v) is not list):
			v = [str(v)]
		for value in v:
			el_filter = ET.SubElement(root, 'field')
			el_filter.set("name", "filter_term")
			el_filter.text = k + ":" + str(value)
	return root

def transform_search_interaction(line):
	(interaction_type, timestamp, session_id, search_term, filters, num_results) = line.split("\t")
	timestamp = timestamp[:-1] # remove trailing 'Z'
	filters = parse_filters(filters)
	return convert_to_xml(interaction_type, timestamp, session_id, search_term, filters, num_results)

def transform_ranked_retrieval(line):
	(interaction_type, timestamp, session_id, search_term, filters, uri, rank_position, num_results) = line.split("\t")
	timestamp = timestamp[:-1]
	filters = parse_filters(filters)
	return convert_to_xml(interaction_type, timestamp, session_id, search_term, filters, num_results, rank_position, uri)

def transform_to_xml(line):
	try:
		operation_type = line.split("\t")[0]
		if(operation_type == "SearchInteraction"):
			return transform_search_interaction(line)
		elif(operation_type == "RankedRetrieveRecordInteraction"):
			return transform_ranked_retrieval(line)
		else:
			return None
	except Exception as a:
		print(str(a) + ": " + line)
		return None

def write_xml(xml_doc, random_session_id):
	random_session_id = random_session_id.replace(".txt", "")
	tree = ET.ElementTree(xml_doc)
	with open(os.path.join(WRITE_DIR, random_session_id + ".xml"), 'w') as xmlout:
		tree.write(xmlout, encoding='unicode')

def serialise_to_xml(xml_list):
	root = ET.Element('add')
	for doc in xml_list:
		root.append(doc)
	return root


xml_structs = []
for f in os.listdir(READ_DIR):
	if(f.endswith(".txt")):
		with open(os.path.join(READ_DIR, f)) as session:
			for line in session.readlines():
				line = line.strip()
				xml_struct = transform_to_xml(line)
				if(xml_struct is not None):
					xml_structs.append(xml_struct)
				if(len(xml_structs) > 100):
					xml_doc = serialise_to_xml(xml_structs)
					write_xml(xml_doc, f)
					xml_structs = []

if(len(xml_structs) > 0):
	xml_doc = serialise_to_xml(xml_structs)
	write_xml(xml_doc, 'FLUSH')
	xml_structs = []

sys.exit()

