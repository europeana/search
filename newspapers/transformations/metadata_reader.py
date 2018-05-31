from pathlib import Path
from urllib.parse import urldefrag, urlparse

import rdflib
import json

"""
see also https://docs.google.com/document/d/1vhQstotXm4b-t8FHCzStHNCoz1dVzGFsaXLrn2vCPVI
"""

supported_langs = ["de", "el", "en", "es", "et", "fi", "fr", "hr", "it", "la", "lv", "nl", "pl", "ru", "sr",
                   "sv", "uk", "ar", "bg", "ca", "cz", "da", "eu", "fa", "ga", "gl", "hi", "hu", "hy", "id",
                   "no", "pt", "ro", "ja", "th", "tr", "ws", "und"]

def _ns_prefix_uri(uriref_str, namespace_dict):
    if '#' in uriref_str:
        url, frag = urldefrag(uriref_str)
        url = url + "#"
    else:
        url_list = uriref_str.rsplit('/', 1)
        url = url_list[0] + "/"
        frag = url_list[1]

    return "%s:%s"%(namespace_dict[url], frag)


class BibliographicResource(object):
    """

    see also current API data fields at
    http://preview.labs.eanadev.org/api/data-fields/

    see also EDM record requirements for creating the IIIF Manifests,
        https://docs.google.com/document/d/1vhQstotXm4b-t8FHCzStHNCoz1dVzGFsaXLrn2vCPVI
    """
    def __int__(self):
        self.europeana_id = ""
        self.issue_id = ""
        self.dc_title = ""
        self.dc_identifier = ""
        self.dcterms_isPartOf = ""
        self.dcterms_issued = ""

        # same as "what" for Aggregated Field/Facet
        # make it language specific ?
        self.dc_type=[]
        # where, location, subject for Aggregated Field/Facet
        self.dcterms_spatial=[]
        # when, subject for Aggregated Field/Facet
        self.dcterms_temporal=[]


        self.aggregation_edm_object = ""
        self.aggregation_edm_aggregatedCHO = ""
        self.aggregation_edm_rights = ""
        # self.*_[lang] e.g., self.dc_type_en, self.dc_type_fr

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_dict(self):
        return self.__dict__


def _add_attr_value_multi(obj, attr, value):
    if not _validate_value(attr, value):
        return

    if hasattr(obj, attr):
        current_value = getattr(obj, attr, [])
        if str(value) not in current_value:
            current_value.append(str(value))

        # reduce duplications
        current_value = list(set(current_value))
        setattr(obj, attr, current_value)
    else:
        setattr(obj, attr, [str(value)])


def _add_attr_value_single(obj, attr, value):
    setattr(obj, attr, value)


def load_edm_in_xml(edm_xml_path):
    """
    load EMD field from edm RDF/XML file

    see also http://preview.labs.eanadev.org/api/data-fields/

    :param edm_xml_path: string
    :return: BibliographicResource| None if file is not exist
    """
    if not Path(edm_xml_path).is_file():
        print(edm_xml_path, " not exist!")
        return None

    graph_in_memory = rdflib.Graph("IOMemory")
    g = graph_in_memory.parse(edm_xml_path,format="xml")

    namespaces = list(g.namespaces())
    # namespaces_dict = dict()
    namespaces_dict = dict([(str(ns), abv) for abv, ns in namespaces])

    predicates = list(g.predicates(None, None))

    bg_resource = BibliographicResource()

    # load resource types
    resource_type_dict = _load_resource_types(g, namespaces_dict, predicates)

    for pred in predicates:
        abbv_pred = _ns_prefix_uri(pred, namespaces_dict)
        subject_object_tuples = g.subject_objects(pred)
        if "rdf:type" == abbv_pred:
            continue

        # print("pred: ", abbv_pred)
        for obj_tuple in subject_object_tuples:
            # print(obj_tuple)
            resource_uri = obj_tuple[0]
            value = obj_tuple[1]

            attr_name = abbv_pred.replace(":","_")

            lang=None
            if isinstance(value, rdflib.term.Literal):
                if hasattr(value, 'language'):
                    lang = value.language
                    # rare case: en-US, e.g., Te%C3%9Fmann_Library\Tiroler_Volksbote\1919-12-24.alto.zip
                    # do we need to differentiate UK english and US english ?
                    if lang is not None and '-' in lang:
                        lang = lang.split('-')[0]

            # attr_name = edm_field_mapping.get(attr_name, attr_name)

            # if resource (i.e.,resource_uri) is a web resource, the property/pred name should start with "wr_*"
            # http://preview.labs.eanadev.org/api/data-fields/#edmwebresource
            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.europeana.eu/schemas/edm/WebResource'):
                # print(resource_uri, " is a web resource!")
                attr_name = "wr_" + attr_name

            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.europeana.eu/schemas/edm/ProvidedCHO'):
                # http://preview.labs.eanadev.org/api/data-fields/#edmprovidedcho
                # print(resource_uri, " is ProvidedCHO!")
                attr_name = "proxy_" + attr_name

            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.openarchives.org/ore/terms/Aggregation'):
                # http://preview.labs.eanadev.org/api/data-fields/#oreaggregation
                if attr_name == "edm:ugc":
                    attr_name = "edm_UGC"
                else:
                    attr_name = "provider_aggregation_" + attr_name

            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.europeana.eu/schemas/edm/Place'):
                # http://preview.labs.eanadev.org/api/data-fields/#edmplace
                attr_name = "pl_" + attr_name

            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept'):
                # http://preview.labs.eanadev.org/api/data-fields/#skosconcept
                attr_name = "cc_" + attr_name

            if resource_uri in resource_type_dict \
                    and resource_type_dict[resource_uri] == rdflib.term.URIRef('http://www.europeana.eu/schemas/edm/TimeSpan'):
                # http://preview.labs.eanadev.org/api/data-fields/#edmTimeSpan
                attr_name = "ts_" + attr_name

            attr_name_lang_specific=None
            if lang:
                attr_name_lang_specific = attr_name+"."+lang

            _add_attr_value_multi(bg_resource, attr_name, value)

            if attr_name_lang_specific:
                _add_attr_value_multi(bg_resource, attr_name_lang_specific, value)

            if 'proxy_dc_title' == attr_name or 'proxy_dc_type' == attr_name or 'proxy_edm_type' == attr_name:
                bg_resource.issue_id = str(resource_uri)

            # newspaper fulltext specific fields
            if 'proxy_dc_format' == attr_name:
                if "[OCR confidence]" in value:
                    ocr_confidence_value = None
                    try:
                        ocr_confidence_value = float(value.replace("[OCR confidence]", "").strip().replace(',','.'))
                    except:
                        print("ocr_confidence value conversion error. ignore this field. Original value: %s" % value)

                    ocr_confidence_attr = "ocr_confidence"
                    if ocr_confidence_value:
                        _add_attr_value_single(bg_resource, ocr_confidence_attr, ocr_confidence_value)


    # print(bg_resource.to_json())
    # print("resource type dictionary: ", resource_type_dict)

    return bg_resource


def _validate_value(attr, value):
    """
    validate value before indexing

    :param value:
    :return:
    """
    if "[OCR confidence]" in str(value):
        return False

    if "proxy_dc_language" == str(attr) and str(value) not in supported_langs:
        return False

    return True


def _load_resource_types(g, namespaces_dict, predicates):
    resource_type_dict = {}
    for pred in predicates:
        abbv_pred = _ns_prefix_uri(pred, namespaces_dict)
        subject_object_tuples = g.subject_objects(pred)
        if "rdf:type" == abbv_pred:
            for obj_tuple in subject_object_tuples:
                resource_type_dict[obj_tuple[0]] = obj_tuple[1]
    return resource_type_dict

# C:\Data\europeana\Te%C3%9Fmann_Library\Tiroler_Volksbote\1919-12-24.alto.zip
# load_edm_in_xml("C:\\Data\\europeana\\%C3%96sterreichische_Nationalbibliothek_-_Austrian_National_Library\\Illustrirtes_Wiener_Extrablatt\\1875-11-17.edm.xml")
