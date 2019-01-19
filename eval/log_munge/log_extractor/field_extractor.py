# extracts which fields are being queried for in 
# (a) the main query term and
# (b) as filters

import os
import re

class FieldExtractor:

	ALLFIELDS = ['COMPLETENESS', 'CONTRIBUTOR', 'COUNTRY', 'CREATOR', 'DATA_PROVIDER', 'LANGUAGE', 'PROVIDER', 'RIGHTS', 'TYPE', 'UGC', 'USERTAGS', 'YEAR', '_version_', 'ag_*', 'ag_dc_date', 'ag_dc_date.*', 'ag_dc_identifier', 'ag_dc_identifier.*', 'ag_dcterms_hasPart', 'ag_dcterms_hasPart.*', 'ag_dcterms_isPartOf', 'ag_dcterms_isPartOf.*', 'ag_edm_begin', 'ag_edm_begin.*', 'ag_edm_end', 'ag_edm_end.*', 'ag_edm_hasMet', 'ag_edm_hasMet.*', 'ag_edm_isRelatedTo', 'ag_edm_isRelatedTo.*', 'ag_foaf_name', 'ag_foaf_name.*', 'ag_owl_sameAs', 'ag_owl_sameAs.*', 'ag_rdagr2_biographicalInformation', 'ag_rdagr2_biographicalInformation.*', 'ag_rdagr2_dateOfBirth', 'ag_rdagr2_dateOfBirth.*', 'ag_rdagr2_dateOfDeath', 'ag_rdagr2_dateOfDeath.*', 'ag_rdagr2_dateOfEstablishment', 'ag_rdagr2_dateOfEstablishment.*', 'ag_rdagr2_dateOfTermination', 'ag_rdagr2_dateOfTermination.*', 'ag_rdagr2_gender', 'ag_rdagr2_gender.*', 'ag_rdagr2_placeOfBirth', 'ag_rdagr2_placeOfBirth.*', 'ag_rdagr2_placeOfDeath', 'ag_rdagr2_placeOfDeath.*', 'ag_rdagr2_professionOrOccupation', 'ag_rdagr2_professionOrOccupation.*', 'ag_skos_altLabel', 'ag_skos_altLabel.*', 'ag_skos_hiddenLabel', 'ag_skos_hiddenLabel.*', 'ag_skos_isRelatedTo.*', 'ag_skos_note', 'ag_skos_note.*', 'ag_skos_prefLabel', 'ag_skos_prefLabel.*', 'cc_*', 'cc_skos_altLabel', 'cc_skos_altLabel.*', 'cc_skos_exactMatch', 'cc_skos_hiddenLabel', 'cc_skos_hiddenLabel.*', 'cc_skos_notation', 'cc_skos_notation.*', 'cc_skos_note', 'cc_skos_note.*', 'cc_skos_prefLabel', 'cc_skos_prefLabel.*', 'contributor', 'date', 'description', 'edm_UGC', 'edm_agent', 'edm_datasetName', 'edm_europeana_aggregation', 'edm_europeana_proxy', 'edm_place', 'edm_previewNoDistribute', 'edm_timespan', 'edm_webResource', 'europeana_aggregation_*', 'europeana_aggregation_dc_creator', 'europeana_aggregation_edm_aggregatedCHO', 'europeana_aggregation_edm_country', 'europeana_aggregation_edm_country.*', 'europeana_aggregation_edm_hasView', 'europeana_aggregation_edm_isShownBy', 'europeana_aggregation_edm_landingPage', 'europeana_aggregation_edm_language', 'europeana_aggregation_edm_language.*', 'europeana_aggregation_edm_preview', 'europeana_collectionName', 'europeana_completeness', 'europeana_id', 'europeana_previewNoDistribute', 'facet_tags', 'filter_tags', 'foaf_organization', 'has_landingpage', 'has_media', 'has_thumbnails', 'identifier', 'is_fulltext', 'org_*', 'org_dc_date', 'org_dc_date.*', 'org_dc_identifier', 'org_dc_identifier.*', 'org_edm_acronym', 'org_edm_acronym.*', 'org_edm_begin', 'org_edm_begin.*', 'org_edm_country', 'org_edm_end', 'org_edm_end.*', 'org_edm_europeanaRole', 'org_edm_europeanaRole.*', 'org_edm_geographicLevel', 'org_edm_geographicLevel.*', 'org_edm_hasMet', 'org_edm_hasMet.*', 'org_edm_isRelatedTo', 'org_edm_isRelatedTo.*', 'org_edm_organizationDomain', 'org_edm_organizationDomain.*', 'org_edm_organizationScope', 'org_edm_organizationScope.*', 'org_edm_organizationSector', 'org_edm_organizationSector.*', 'org_foaf_name', 'org_foaf_name.*', 'org_owl_sameAs', 'org_owl_sameAs.*', 'org_rdagr2_biographicalInformation', 'org_rdagr2_biographicalInformation.*', 'org_rdagr2_dateOfBirth', 'org_rdagr2_dateOfBirth.*', 'org_rdagr2_dateOfDeath', 'org_rdagr2_dateOfDeath.*', 'org_rdagr2_dateOfEstablishment', 'org_rdagr2_dateOfEstablishment.*', 'org_rdagr2_dateOfTermination', 'org_rdagr2_dateOfTermination.*', 'org_rdagr2_gender', 'org_rdagr2_gender.*', 'org_rdagr2_professionOrOccupation', 'org_rdagr2_professionOrOccupation.*', 'org_skos_altLabel', 'org_skos_altLabel.*', 'org_skos_hiddenLabel', 'org_skos_hiddenLabel.*', 'org_skos_note', 'org_skos_note.*', 'org_skos_prefLabel', 'org_skos_prefLabel.*', 'pl_*', 'pl_dcterms_hasPart', 'pl_dcterms_hasPart.*', 'pl_dcterms_isPartOf', 'pl_dcterms_isPartOf.*', 'pl_owl_sameAs.*', 'pl_skos_altLabel', 'pl_skos_altLabel.*', 'pl_skos_hasPart.*', 'pl_skos_hiddenLabel', 'pl_skos_hiddenLabel.*', 'pl_skos_isPartOf.*', 'pl_skos_note', 'pl_skos_note.*', 'pl_skos_prefLabel', 'pl_skos_prefLabel.*', 'pl_wgs84_pos_alt', 'pl_wgs84_pos_lat', 'pl_wgs84_pos_lat_long', 'pl_wgs84_pos_long', 'provider_aggregation_*', 'provider_aggregation_cc_deprecated_on', 'provider_aggregation_cc_license', 'provider_aggregation_dc_rights', 'provider_aggregation_dc_rights.*', 'provider_aggregation_edm_aggregatedCHO', 'provider_aggregation_edm_dataProvider', 'provider_aggregation_edm_dataProvider.*', 'provider_aggregation_edm_hasView', 'provider_aggregation_edm_intermediateProvider', 'provider_aggregation_edm_intermediateProvider.*', 'provider_aggregation_edm_isShownAt', 'provider_aggregation_edm_isShownBy', 'provider_aggregation_edm_object', 'provider_aggregation_edm_provider', 'provider_aggregation_edm_provider.*', 'provider_aggregation_edm_rights', 'provider_aggregation_edm_rights.*', 'provider_aggregation_odrl_inherited_from', 'proxy_*', 'proxy_dc_contributor', 'proxy_dc_contributor.*', 'proxy_dc_coverage', 'proxy_dc_coverage.*', 'proxy_dc_creator', 'proxy_dc_creator.*', 'proxy_dc_date', 'proxy_dc_date.*', 'proxy_dc_description', 'proxy_dc_description.*', 'proxy_dc_format', 'proxy_dc_format.*', 'proxy_dc_identifier', 'proxy_dc_identifier.*', 'proxy_dc_language', 'proxy_dc_language.*', 'proxy_dc_publisher', 'proxy_dc_publisher.*', 'proxy_dc_relation', 'proxy_dc_relation.*', 'proxy_dc_rights', 'proxy_dc_rights.*', 'proxy_dc_source', 'proxy_dc_source.*', 'proxy_dc_subject', 'proxy_dc_subject.*', 'proxy_dc_title', 'proxy_dc_title.*', 'proxy_dc_type', 'proxy_dc_type.*', 'proxy_dc_type_search', 'proxy_dcterms_alternative', 'proxy_dcterms_alternative.*', 'proxy_dcterms_conformsTo', 'proxy_dcterms_conformsTo.*', 'proxy_dcterms_created', 'proxy_dcterms_created.*', 'proxy_dcterms_extent', 'proxy_dcterms_extent.*', 'proxy_dcterms_hasFormat', 'proxy_dcterms_hasFormat.*', 'proxy_dcterms_hasPart', 'proxy_dcterms_hasPart.*', 'proxy_dcterms_hasVersion', 'proxy_dcterms_hasVersion.*', 'proxy_dcterms_isFormatOf', 'proxy_dcterms_isFormatOf.*', 'proxy_dcterms_isPartOf', 'proxy_dcterms_isPartOf.*', 'proxy_dcterms_isReferencedBy', 'proxy_dcterms_isReferencedBy.*', 'proxy_dcterms_isReplacedBy', 'proxy_dcterms_isReplacedBy.*', 'proxy_dcterms_isRequiredBy', 'proxy_dcterms_isRequiredBy.*', 'proxy_dcterms_isRequiredby.*', 'proxy_dcterms_isVersionOf', 'proxy_dcterms_isVersionOf.*', 'proxy_dcterms_issued', 'proxy_dcterms_issued.*', 'proxy_dcterms_medium', 'proxy_dcterms_medium.*', 'proxy_dcterms_provenance', 'proxy_dcterms_provenance.*', 'proxy_dcterms_references', 'proxy_dcterms_references.*', 'proxy_dcterms_replaces', 'proxy_dcterms_replaces.*', 'proxy_dcterms_requires', 'proxy_dcterms_requires.*', 'proxy_dcterms_spatial', 'proxy_dcterms_spatial.*', 'proxy_dcterms_tableOfContents', 'proxy_dcterms_tableOfContents.*', 'proxy_dcterms_temporal', 'proxy_dcterms_temporal.*', 'proxy_edm_hasMet', 'proxy_edm_hasMet.*', 'proxy_edm_hasType', 'proxy_edm_hasType.*', 'proxy_edm_incorporates', 'proxy_edm_incorporates.*', 'proxy_edm_isDerivativeOf', 'proxy_edm_isDerivativeOf.*', 'proxy_edm_isNextInSequence', 'proxy_edm_isRelatedTo', 'proxy_edm_isRelatedTo.*', 'proxy_edm_type', 'proxy_edm_year.*', 'proxy_ore_proxy', 'proxy_owl_sameAs', 'skos_concept', 'source', 'subject', 'sv_dcterms_conformsTo', 'sv_doap_implements', 'svcs_service', 'text', 'timestamp', 'timestamp_*', 'title', 'ts_*', 'ts_dcterms_hasPart', 'ts_dcterms_hasPart.*', 'ts_dcterms_isPartOf', 'ts_dcterms_isPartOf.*', 'ts_edm_begin', 'ts_edm_begin.*', 'ts_edm_end', 'ts_edm_end.*', 'ts_owl_sameAs.*', 'ts_skos_altLabel', 'ts_skos_altLabel.*', 'ts_skos_hiddenLabel', 'ts_skos_hiddenLabel.*', 'ts_skos_note', 'ts_skos_note.*', 'ts_skos_prefLabel', 'ts_skos_prefLabel.*', 'what', 'when', 'where', 'who', 'wr_*', 'wr_cc_deprecated_on', 'wr_cc_license', 'wr_dc_creator', 'wr_dc_creator.*', 'wr_dc_description', 'wr_dc_description.*', 'wr_dc_format', 'wr_dc_format.*', 'wr_dc_rights', 'wr_dc_rights.*', 'wr_dc_source', 'wr_dc_source.*', 'wr_dc_type', 'wr_dc_type.*', 'wr_dcterms_conformsTo', 'wr_dcterms_conformsTo.*', 'wr_dcterms_created', 'wr_dcterms_created.*', 'wr_dcterms_extent', 'wr_dcterms_extent.*', 'wr_dcterms_hasPart', 'wr_dcterms_hasPart.*', 'wr_dcterms_isFormatOf', 'wr_dcterms_isFormatOf.*', 'wr_dcterms_isPartOf', 'wr_dcterms_isPartOf.*', 'wr_dcterms_isReferencedBy', 'wr_dcterms_issued', 'wr_dcterms_issued.*', 'wr_edm_isNextInSequence', 'wr_edm_preview', 'wr_edm_rights', 'wr_edm_rights.*', 'wr_odrl_inherited_from', 'wr_svcs_hasservice']

	def __init__(self):
		self.entry_directory = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'entries_by_session')
		self.fields_directory = os.path.join(os.path.dirname(__file__), 'final_output', 'fields')	
		self.query_fields = {}
		self.filter_fields = {}

	def do_extraction(self):
		self.extract_fields()
		self.output_fields()

	def extract_fields(self):
		for filename in os.listdir(self.entry_directory):
			with open(os.path.join(self.entry_directory, filename)) as inf:
				for line in inf.readlines():
					try:
						(searchtype, _, _, searchterms, filterterms, _) = line.split("\t")
						if(searchtype == "SearchInteraction"):
							self.extract_query_fields(searchterms)
							self.extract_filter_fields(filterterms)
					except ValueError:
						pass

	def extract_query_fields(self, terms_query):
		for term in terms_query.split():
			if(":" in term):
				field = term.split(":")[0]
				if("." in field):
					field = field.split(".")[0] + ".*"
				if(field in FieldExtractor.ALLFIELDS):
					try:
						self.query_fields[field] += 1
					except KeyError:
						self.query_fields[field] = 1

	def extract_filter_fields(self, filter_queries):
		for term in filter_queries.split("':"):
			term = term.split("'")[-1]
			trimmed = re.sub(r'[\W]', '', term)
			if(trimmed == ""):
				continue
			if("." in trimmed):		
				trimmed = trimmed.split(".")[0] + ".*"
			if(trimmed in FieldExtractor.ALLFIELDS):
				try:
					self.filter_fields[trimmed] += 1
				except KeyError:
					self.filter_fields[trimmed] = 1

	def output_fields(self):
		with open(os.path.join(self.fields_directory, 'queries.txt'), 'w') as qout:
			for k in sorted(self.query_fields.keys()):
				count = str(self.query_fields[k]) 
				msg = k + "\t" + count + "\n"
				qout.write(msg)

		with open(os.path.join(self.fields_directory, 'filters.txt'), 'w') as fout:
			for k in sorted(self.filter_fields.keys()):
				count = str(self.filter_fields[k]) 
				msg = k + "\t" + count + "\n"
				fout.write(msg)
