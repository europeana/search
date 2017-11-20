from django.shortcuts import render
from django.http import HttpResponse
import xml.etree.ElementTree as ET
from collectionbuilder.xmlutil import XMLQueryEditor
from collectionbuilder.xmlutil.InconsistentOperatorException import InconsistentOperatorException
from collectionbuilder.xmlutil.ZeroResultsException import ZeroResultsException
import copy
import requests
import json
import re
import os

XQE = XMLQueryEditor.XMLQueryEditor()
# TODO: we're going to want to load this from a config file 
# at some point
ALL_FIELDS = []
FACET_FIELDS = []
SOLR_URL = "http://sol7.eanadev.org:9191/solr/search_production_publish_1/select?wt=json"
EXPANSION_LANGUAGES = ["fr", "de", "es", "nl", "pl", "it", "bg", "hu", "cs", "da", "et", "fi", "el", "hr", "ga", "lt", "lv", "pt", "ro", "sk", "sl", "sv", "hr", "mt", "el", "la", "gd", "ru", "ca", "cu"]

def index(request):
	here = os.path.dirname(os.path.realpath(__file__))
	allfields_path = os.path.join(here, "conf", "allfields.txt")
	facetfields_path = os.path.join(here, "conf", "facetfields.txt")
	with open(allfields_path) as allfields:
		for line in allfields.readlines():
			ALL_FIELDS.append(line.strip())
	with open(facetfields_path) as facetfields:
		for line in facetfields.readlines():
			FACET_FIELDS.append(line.strip())
	return render(request, 'collectionbuilder/index.html')

def init(request):
	global XQE
	XQE = XMLQueryEditor.XMLQueryEditor()
	tree = copy.deepcopy(XQE.get_tree().getroot())
	for clause in tree.findall(".//clause"):
		append_all_fields(clause)
	return HttpResponse(ET.tostring(tree), 'application/xml')

def getfullquery(request):
	return HttpResponse(ET.tostring(XQE.get_tree().getroot()), 'application/xml')

def newclause(request):
	node_id = request.GET["node_id"]
	new_clause = XQE.generate_clause()
	XQE.add_clausular_element(new_clause, node_id)
	dec_clause = copy.deepcopy(new_clause)
	append_all_fields(dec_clause)
	return HttpResponse(ET.tostring(dec_clause), 'application/xml')

def newclausegroup(request):
	node_id = request.GET["node_id"]
	new_clause_group = XQE.generate_clause_group()
	new_clause = XQE.generate_clause()
	group_id = new_clause_group.attrib["node-id"]
	XQE.add_clausular_element(new_clause_group, node_id)
	XQE.add_clausular_element(new_clause, group_id)
	dec_group = copy.deepcopy(XQE.retrieve_node_by_id(group_id))
	dec_clause = dec_group.find("./clause")
	append_all_fields(dec_clause)
	return HttpResponse(ET.tostring(dec_group), 'application/xml')

def newexpansiongroup(request):
	node_id = request.GET["node_id"]
	translations = request.GET["translations"].split(",")
	field_name = request.GET["fieldname"]
	new_clause_group = XQE.generate_clause_group()
	parent_id = new_clause_group.attrib["node-id"]
	XQE.add_clausular_element(new_clause_group, node_id)
	for translation in translations:
		new_clause = XQE.generate_clause(operator="OR", field=field_name, value=translation)
		XQE.add_clausular_element(new_clause, parent_id)
	return HttpResponse(ET.tostring(new_clause_group), 'application/xml')

def deleteclelement(request):
	node_to_remove = request.GET["node_to_remove"]
	node_to_reflow = request.GET["node_to_reflow"]
	if(node_to_reflow == "0"):
		XQE.remove_node_from_root(node_to_remove)
		reflow_node = copy.deepcopy(XQE.get_tree().getroot())
	else:
		XQE.remove_node_by_id(node_to_remove)
		reflow_node = copy.deepcopy(XQE.retrieve_node_by_id(node_to_reflow))
	append_all_fields(reflow_node)
	return HttpResponse(ET.tostring(reflow_node), 'application/xml')

def facetvalues(request):
	node_id = request.GET["node_id"]
	current_field = request.GET["current_field"]
	all_values = {}
	if(current_field not in FACET_FIELDS):
		all_values["values"] = ["Application Message: N/A"]
		return HttpResponse(json.dumps(all_values), 'application/json')
	current_value = request.GET["current_value"]
	XQE.set_field(current_field, node_id)
	XQE.set_value(current_value, node_id)
	fq = XQE.get_facet_query_for_clause(node_id)
	slr_qry = SOLR_URL + "&q=" + fq + "&rows=0&facet=true&facet.mincount=1&facet.limit=1250&facet.field=" + current_field
	res = requests.get(slr_qry).json()
	try:
		values_list = [val for val in res["facet_counts"]["facet_fields"][current_field] if re.search('[a-zA-Z]', str(val))]
		count_list = [c for c in res["facet_counts"]["facet_fields"][current_field] if re.match('^[\d]+$', str(c))]
		all_values["values"] = values_list[:1000]
		print(count_list)
	except KeyError:
		error_msg = ["ERROR", res["error"]["msg"]]
		all_values["values"] = error_msg
	except Exception as e:
		all_values["values"] = ["ERROR", "Unidentified error in making query: " + str(e)]
	return HttpResponse(json.dumps(all_values), 'application/json')
	

def translate(request):
	term = request.GET["term"]
	wkdt_termsearch = "https://www.wikidata.org/w/api.php?format=json&action=wbsearchentities&language=en&limit=1&search=" + term
	termsearch_as_json = requests.get(wkdt_termsearch).json()
	success = (termsearch_as_json['success'] == 1 and len(termsearch_as_json["search"]) > 0)
	terms = {}
	if(success):
		entity_id = termsearch_as_json["search"][0]["id"]
		wkdt_idsearch = "https://www.wikidata.org/w/api.php?format=json&action=wbgetentities&props=labels&ids=" + entity_id
		idsearch_as_json = requests.get(wkdt_idsearch).json()
		inner_success = idsearch_as_json['success'] == 1 and len(idsearch_as_json['entities']) > 0
		if(inner_success):
			labels = idsearch_as_json['entities'][entity_id]['labels']
			for lang in EXPANSION_LANGUAGES:
			 if lang in labels:
			 	trans_term = labels[lang]["value"]
			 	terms[lang] = trans_term
	return HttpResponse(json.dumps(terms), 'application/json')

def updateoperator(request):
	newop = request.GET["operator"]
	node_id = request.GET["node_id"]
	try:
		XQE.set_operator(newop, node_id)
		return HttpResponse(ET.tostring(XQE.get_tree().getroot()), 'application/xml')
	except InconsistentOperatorException as ioe:
		return HttpResponse("<warning>Inconsistent Operators</warning>", 'application/xml')
	except ZeroResultsException as zre:
		return HttpResponse("<warning>Zero Results</warning>", 'application/xml')


def updatenegated(request):
	newneg = request.GET["negstatus"]
	node_id = request.GET["node_id"]
	if(newneg == "negated"):
		XQE.negate_by_id(node_id)
	else:
		XQE.unnegate_by_id(node_id)
	return HttpResponse(ET.tostring(XQE.get_tree().getroot()), 'application/xml')

def append_all_fields(new_clause):
	all_fields_piggyback = ET.fromstring("<all-fields></all-fields>")
	all_fields_piggyback.text = ",".join(ALL_FIELDS)
	clause_type = new_clause.tag 
	if(clause_type == "clause"):
		new_clause.append(all_fields_piggyback)
	elif(clause_type == "clause-group"):
		for child in new_clause:
			append_all_fields(child)

def updatevalues(request):
	clause_id = request.GET["node_id"]
	field = request.GET["field_name"]
	value = request.GET["field_value"]
	XQE.set_field(field, clause_id)
	XQE.set_value(value, clause_id)
	return HttpResponse(ET.tostring(XQE.get_tree().getroot()), 'application/xml')

def changedeprecate(request):
	node_id = request.GET["node_id"]
	operation = request.GET["depstatus"]
	if(operation == "deprecate"):
		XQE.deprecate_by_id(node_id)
	else:
		XQE.undeprecate_by_id(node_id)
	return HttpResponse(ET.tostring(XQE.get_tree().getroot()), 'application/xml')

def converttoclausegroup(request):
	node_id = request.GET["node_id"]
	group_parent = copy.deepcopy(XQE.convert_to_clause_group(node_id))
	for clause in group_parent.findall(".//clause"):
		append_all_fields(clause)
	return HttpResponse(ET.tostring(group_parent), 'application/xml')

def converttoclause(request):
	node_id = request.GET["node_id"]
	try:
		group_parent = copy.deepcopy(XQE.ungroup_clause_group(node_id))
		for clause in group_parent.findall(".//clause"):
			append_all_fields(clause)
		return HttpResponse(ET.tostring(group_parent), 'application/xml')
	except InconsistentOperatorException as ioe:
		return HttpResponse("<warning>Inconsistent Operators</warning>", 'application/xml')	

def forcealloperators(request):
	node_id = request.GET["node_id"]
	new_operator = request.GET["operator"]
	try:
		group_parent = copy.deepcopy(XQE.set_all_operators(new_operator, node_id))
		for clause in group_parent.findall(".//clause"):
			append_all_fields(clause)
		return HttpResponse(ET.tostring(group_parent), 'application/xml')
	except ZeroResultsException as zre:
		return HttpResponse("<warning>Zero Results</warning>", 'application/xml')	

def getsavedqueries(request):
	return HttpResponse(json.dumps(XQE.read_query_directory()), 'application/json')

def savequery(request):
	query_name = request.GET["query_name"]
	XQE.save_query_file(query_name)
	return HttpResponse("<status>success</status>", 'application/xml')

def gethitcount(request):
	try:
		count = XQE.postflight_query()
		return HttpResponse(json.dumps({ 'count' : count }), 'application/json')
	except:
		return HttpResponse(json.dumps({'status':'false','message':'Connection failure'}), 'application/json')


def openquery(request):
	query_name = request.GET["query_name"]
	global XQE
	XQE = XMLQueryEditor.XMLQueryEditor(query_name)
	tree = copy.deepcopy(XQE.get_tree().getroot())
	for clause in tree.findall(".//clause"):
		append_all_fields(clause)
	return HttpResponse(ET.tostring(tree), 'application/xml')

def instructions(request):
    return render(request, 'collectionbuilder/instructions.html')