import json

import os
import time
from pathlib import Path
import rdflib
from datetime import datetime
import re, random
from urllib.parse import urldefrag

from etl_util import ns_prefix_uri, add_attr_value_single, load_resource_types


class EDMFullTextResource(object):
    """
    EDM fulltext data model corresponding to Solr document

    """
    def __init__(self, dataset_id, record_id, page_no):
        self.fulltext_id = "/%s/%s/%s" % (dataset_id, record_id, page_no)
        # metadata id
        self.europeana_id = ""
        # Holds the URL of the image
        self.edm_webResource = []
        # Holds the URL of the edm:FullTextResource
        self.fulltextresource = ""
        # Average Page confidence
        self.nif_confidence = ""
        # dc_type (default to 'page')
        self.dc_type = "Page"
        self.page_number = page_no
        self.fulltext = ""
        self.language = ""

    def set_fulltext_id(self, metadata_id, page_no):
        self.fulltext_id = "%s/%s" % (metadata_id, page_no)

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_edm_json(self):
        newspaper_fulltext = self.__dict__

        # language specific field
        if self.language != "":
            #language_specific_fulltext_attr = "fulltext." + self.language
            #dd_attr_value_single(newspaper_fulltext, language_specific_fulltext_attr, self.fulltext)
            lang = self.language
            if lang == "en-US":
                lang = "en"
            newspaper_fulltext["fulltext." + lang] = self.fulltext
            del newspaper_fulltext['fulltext']

        record_created_time = datetime.utcnow().replace(microsecond=0).isoformat()
        newspaper_fulltext['timestamp_created'] = record_created_time
        newspaper_fulltext['timestamp_update'] = record_created_time

        return newspaper_fulltext

    def to_dict(self):
        return self.__dict__


def _correct_edm_content(rdf_xml_content):
    """
    Current EDM fulltext RDF is not a valid RDF resource

    Two problems in 'oa:Annotation': 1) rdf:ID does not start from character;
                2) rdf:ID is duplicated if two annotations are applied for same string (word or line)

    This method is a workaround to make it as a valid RDF data (in order to process it as a RDF)

    :param rdf_xml_content:
    :return:
    """
    return re.sub("<oa:Annotation rdf:ID=\"/", lambda x: "<oa:Annotation rdf:ID=\"ID%s%s_" % (random.randint(10,999),random.randint(10,999)),rdf_xml_content)
    # return re.sub("<oa:Annotation rdf:ID=\"/", lambda x: "<oa:Annotation rdf:ID=\"ID"+str(random.randint(10,999))


def load_valid_rdf_content(edm_xml_path):
    """
    load RDF/XML content from file and make sure the content is a valid RDF resource

    :param edm_xml_path:
    :return:
    """
    with open(edm_xml_path,"r", encoding='utf-8') as f:
        content = f.read()

    return _correct_edm_content(content)


def extract_europeana_id(fulltextresource):
    """
    extract fulltext issue id (i.e., europeana_id) from fulltext resource id

    issue id is the fulltext resource URI excluding the suffix part and fulltext namespace

    Format: '/{DATASET_ID}/{RECORD_ID}'

    :param fulltextresource:
    :return:
    """
    fulltext_id = os.path.basename(fulltextresource)
    data_uri = "http://data.europeana.eu/fulltext"
    return fulltextresource.replace(data_uri,"").replace("/"+fulltext_id,"")


def extract_edm_webresource(targetURL):
    """
    extract image URL from word annotation target URL
    
    A simple approach to get page image URI instead of checking if annotation type is "Page"
    :param param:
    :return:
    """
    return targetURL.split("#")[0]


def load_edm_in_xml(edm_xml_path):
    if not Path(edm_xml_path).is_file():
        print(edm_xml_path, " not exist!")
        return None

    page_no = os.path.basename(edm_xml_path).split(".")[0]
    edm_xml_content = load_valid_rdf_content(edm_xml_path)

    return extract_edm_fulltext_model(edm_xml_content, page_no)


def extract_edm_fulltext_model(edm_xml_content, page_no):
    """

    :param edm_xml_content: Fulltext EDM RDF/XML raw content
    :param page_no: page no (extractable from file name)
    :return: EDMFullTextResource, EDM data model for Solr
    """
    graph_in_memory = rdflib.Graph("IOMemory")
    # g = graph_in_memory.parse(edm_xml_path,format="xml")
    g = graph_in_memory.parse(data=_correct_edm_content(edm_xml_content), format="xml")

    namespaces = list(g.namespaces())
    namespaces_dict = dict([(str(ns), abv) for abv, ns in namespaces])
    # predicates = list(g.predicates(None, None))
    # print(predicates)
    ft_resource = EDMFullTextResource("", "", page_no)
    # load resource types (take around 4 seconds)
    resource_type_dict = load_resource_types(g, namespaces_dict)

    word_confidences = []
    for subject, predicate, object in g:
        abbv_pred = ns_prefix_uri(predicate, namespaces_dict)
        # print(subject, abbv_pred, object)
        if "rdf:type" == abbv_pred:
            continue

        if ft_resource.fulltextresource == "" and \
                str(subject) in resource_type_dict and \
                resource_type_dict[str(subject)] == "http://www.europeana.eu/schemas/edm/FullTextResource":
            ft_resource.fulltextresource = str(subject)

        if ft_resource.fulltext == "" and \
                str(subject) in resource_type_dict and \
                resource_type_dict[str(subject)] == "http://www.europeana.eu/schemas/edm/FullTextResource" and \
                abbv_pred == "rdf:value":
            ft_resource.fulltext = str(object)

        if abbv_pred == "dc:language":
            ft_resource.language = str(object)

        if abbv_pred == "nif:confidence":
            word_confidences.append(float(str(object)))

        if abbv_pred == "oa:hasTarget" and len(ft_resource.edm_webResource) == 0:
            edm_webResource = extract_edm_webresource(str(object))
            ft_resource.edm_webResource = [edm_webResource]

    if len(word_confidences) > 0:
        ft_resource.nif_confidence = float(sum(word_confidences) / len(word_confidences))

    if ft_resource.fulltextresource != "":
        ft_resource.europeana_id = extract_europeana_id(ft_resource.fulltextresource)
        ft_resource.set_fulltext_id(ft_resource.europeana_id, ft_resource.page_number)

    return ft_resource


#start_time = time.time()
#edm_model = load_edm_in_xml("C:\\Data\\europeana\\newspapers\\fulltext\\edm\\9200396\\BibliographicResource_3000118436329\\45.xml")
#print("--- %s seconds ---" % (time.time() - start_time))
#edm_model = load_edm_in_xml("C:\\Data\\europeana\\newspapers\\fulltext\\edm\\9200396\\BibliographicResource_3000118436329\\22.xml")
#print(edm_model.to_edm_json())
#print(not is_ncname("/35d2d91d706860e30e9dff101921347d"))