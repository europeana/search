import xml.etree.ElementTree as ET
import os
import re
import sys
import pdb


READ_DIR = '/media/mmarrero/data/SearchEvaluation/April2020/28Nov19_1Feb2020/entries_by_session'
WRITE_DIR = '/media/mmarrero/data/SearchEvaluation/April2020/28Nov19_1Feb2020/as_xml'

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

def strip_illegal_characters(raw_term):
	illegal_xml_re = re.compile(u'[\x00-\x08\x0b-\x1f\x7f-\x84\x86-\x9f\ud800-\udfff\ufdd0-\ufddf\ufffe-\uffff]')
	term = illegal_xml_re.sub(raw_term, '')
	return term

def strip_illegal_characters_monica2(raw_term):
	illegal_xml_re = re.compile(u'[\x00-\x08\x0b-\x1f\x7f-\x84\x86-\x9f\ud800-\udfff\ufdd0-\ufddf\ufffe-\uffff]')
	term = illegal_xml_re.sub('',raw_term)
	return term

def strip_illegal_characters_monica(raw_term):
	_illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), (0x7F, 0x84), (0x86, 0x9F), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)]
	if sys.maxunicode >= 0x10000:  # not narrow build 
		_illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),(0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),(0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),(0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),(0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),(0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),(0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),(0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)])
	_illegal_ranges = ["%s-%s" % (chr(low), chr(high)) for (low, high) in _illegal_unichrs] 
	_illegal_xml_chars_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges)) 
	term = re.sub(_illegal_xml_chars_RE, '', raw_term)
	return term

def convert_to_xml(interaction_type, timestamp, session_id, search_term, filters, num_results, rank_position=-1, uri=None):
	#pdb.set_trace()
	timestamp = strip_illegal_characters_monica(timestamp)
	session_id = strip_illegal_characters_monica(session_id)
	search_term = strip_illegal_characters_monica(search_term)
	num_results = strip_illegal_characters_monica(num_results)
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
	
#	el_id = ET.SubElement(root, 'field')
#	el_id.set("name", "id") #automatically added in Solr according to solrconfig.xml

	
	el_search_term = ET.SubElement(root, 'field')
	el_search_term.set("name", "query_term")
	el_search_term.text = search_term
	el_num_results = ET.SubElement(root, 'field')
	el_num_results.set("name", "total_results")
	el_num_results.text = str(num_results)
	if(int(rank_position) > -1):
		el_rank_position = ET.SubElement(root, 'field')
		el_rank_position.set("name", "rank_position")
		el_rank_position.text = str(rank_position)
	if(uri is not None):
		uri = strip_illegal_characters_monica(uri)
		el_uri = ET.SubElement(root, 'field')
		el_uri.set("name", "uri")
		uri = "http://www.europeana.eu/portal/en/record" + uri
		el_uri.text = uri
	for k, v in filters.items():
		if(type(v) is not list):
			v = [str(v)]
		for value in v:
			value = strip_illegal_characters_monica(value)
			el_filter = ET.SubElement(root, 'field')
			el_filter.set("name", "filter_term")
			el_filter.text = k + ":" + str(value)
	return root

def transform_search_interaction(line):
	(interaction_type, timestamp, session_id, search_term, filters, num_results) = line.split("\t")
	#timestamp = timestamp[:-5] # remove trailing ms + 'Z'
	filters = parse_filters(filters)
	return convert_to_xml(interaction_type, timestamp, session_id, search_term, filters, num_results)

def transform_ranked_retrieval(line):
	(interaction_type, timestamp, session_id, search_term, filters, uri, rank_position, num_results) = line.split("\t")
	#timestamp = timestamp[:-5]
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

