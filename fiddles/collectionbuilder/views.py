from django.shortcuts import render
from django.http import HttpResponse
import xml.etree.ElementTree as ET
from collectionbuilder.xmlutil import XMLQueryEditor
from collectionbuilder.xmlutil.InconsistentOperatorException import InconsistentOperatorException
import copy
import requests
import json
import re

XQE = XMLQueryEditor.XMLQueryEditor()
# TODO: we're going to want to load this from a config file 
# at some point
ALL_FIELDS = ["text","europeana_collectionName","edm_datasetName","has_thumbnails", "provider_aggregation_edm_isShownBy","who","when","what","where","subject","PROVIDER","DATA_PROVIDER","is_fulltext", "has_media","filter_tags","facet_tags","has_landingpage","timestamp","europeana_id","title","europeana_completeness","CREATOR","CONTRIBUTOR","UGC","LANGUAGE","TYPE","YEAR","COUNTRY","RIGHTS","COMPLETENESS","edm_previewNoDistribute","provider_aggregation_edm_dataProvider","_aggregation_edm_hasView", "provider_aggregation_edm_isShownAt","provider_aggregation_edm_object","provider_aggregation_edm_provider","_aggregation_dc_rights","provider_aggregation_edm_rights","provider_aggregation_edm_intermediateProvider","europeana_aggregation_edm_country","europeana_aggregation_edm_language","dm_webResource","wr_dc_rights","wr_edm_rights","wr_edm_isNextInSequence","proxy_dc_contributor","proxy_dc_coverage","proxy_dc_creator","proxy_dc_date","proxy_dc_description","proxy_dc_language","proxy_dc_subject","proxy_dc_format","proxy_dc_title","proxy_dc_type","proxy_dc_type_search","proxy_dc_source","proxy_dc_rights","proxy_dc_identifier","proxy_dcterms_created","proxy_dcterms_issued","proxy_dcterms_spatial","proxy_dcterms_temporal","proxy_dc_publisher","proxy_dcterms_hasPart","proxy_dcterms_isPartOf","proxy_dcterms_provenance","proxy_dcterms_medium","proxy_dcterms_alternative","proxy_edm_type","dm_UGC","edm_agent","ag_skos_prefLabel","ag_skos_altLabel","ag_foaf_name","edm_timespan","ts_skos_prefLabel","ts_skos_altLabel","edm_place","pl_skos_prefLabel","pl_skos_altLabel","pl_wgs84_pos_lat","pl_wgs84_pos_long","pl_wgs84_pos_alt","skos_concept","cc_skos_prefLabel","cc_skos_altLabel","provider_aggregation_cc_license","provider_aggregation_odrl_inherited_from","wr_cc_license","wr_cc_deprecated_on","foaf_organization","org_skos_prefLabel","org_skos_altLabel","_version_","svcs_service","sv_dcterms_conformsTo","wr_svcs_hasservice","proxy_edm_currentLocation","proxy_edm_hasMet","proxy_edm_isRelatedTo","proxy_edm_year","ag_rdagr2_dateOfBirth","ag_rdagr2_dateOfDeath","ag_rdagr2_professionOrOccupation","ag_rdagr2_placeOfBirth","ag_rdagr2_placeOfDeath","wr_cc_odrl_inherited_from","provider_aggregation_cc_deprecated_on","wr_dcterms_isReferencedBy"]
SOLR_URL = "http://sol7.eanadev.org:9191/solr/search_production_publish_1/select?wt=json"
EXPANSION_LANGUAGES = ["fr", "de", "es", "nl", "pl", "it"] #TODO: get more codes

def index(request):
	return render(request, 'collectionbuilder/index.html')

def init(request):
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
	current_value = request.GET["current_value"]
	XQE.set_field(current_field, node_id)
	XQE.set_value(current_value, node_id)
	fq = XQE.get_facet_query_for_clause(node_id)
	slr_qry = SOLR_URL + "&q=" + fq + "&rows=0&facet=true&facet.mincount=1&facet.limit=250&facet.field=" + current_field
	res = requests.get(slr_qry).json()
	values_list = [val for val in res["facet_counts"]["facet_fields"][current_field] if re.search('[a-zA-Z]', str(val))]
	all_values = {}
	all_values["values"] = values_list
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
	group_parent = copy.deepcopy(XQE.set_all_operators(new_operator, node_id))
	for clause in group_parent.findall(".//clause"):
		append_all_fields(clause)
	return HttpResponse(ET.tostring(group_parent), 'application/xml')	

def instructions(request):
    return render(request, 'collectionbuilder/instructions.html')