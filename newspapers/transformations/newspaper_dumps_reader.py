#!/usr/bin/env python
# Usage: python newspaper_dumps_reader.py <solr_server_url> <dataset_type> ("metadata"| "fulltext") <newspaper_library_directory>

import os
import threading
import multiprocessing
from multiprocessing import Pool
from itertools import repeat

import zipfile
from SolrClient import SolrClient, SolrError
from metadata_reader import load_edm_in_xml, extract_edm_metadata_model, BibliographicResource
from alto_ocr_text import extract_fulltext_4_issue
from etl_util import load_files_path_from_dir, load_all_files_from_zip_file, extract_file_name, load_all_files_from_dir
from edm_fulltext_reader import extract_edm_fulltext_model

solrClient = SolrClient("http://144.76.218.178:9192/solr/fulltext")

# global statistics
invalid_fulltext_file = 0
fulltext_without_edm_metadata = 0
fulltext_without_page_level_lang = 0
total_page_indexed = 0

# Define the maximum number of cpu cores to use
MAX_PROCESSES = multiprocessing.cpu_count()


class AtomicBulkDocCache:
    def __init__(self, initial=list()):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.buffer = initial
        self._lock = threading.Lock()
        self.value = 0

    def add_new(self, doc_json):
        with self._lock:
            self.buffer.append(doc_json)
            self.value += 1
            return self.buffer

    def clean_top_n(self, top_n=100):
        with self._lock:
            del self.buffer[:top_n]


def load_all_issues_alto_fulltext(newspaper_dir):
    """
    load ALTO fulltext file path from newspaper issue directory

    usage: le_temps_full_text = load_issue_alto_files("/europeana-research-newspapers-dump-2nd/National_Library_of_France/Le_Temps")

    :param issue_dir:
    :return:
    """
    return load_files_path_from_dir(newspaper_dir, file_suffix=".alto.zip")


def load_all_newspapers_from_provider(provider_dir):
    all_newspapers_dir = []
    for newspaper_dir in os.listdir(provider_dir):
        newspaper_abs_dir = os.path.join(provider_dir, newspaper_dir)
        if os.path.isdir(newspaper_abs_dir):
            all_newspapers_dir.append(newspaper_abs_dir)
    return all_newspapers_dir


def _get_edm_xml_file(alto_zip_file_path):
    """

    hard code for consistency file names in Netherlands library, e.g., 'National_Library_of_the_Netherlands/Journal_d%27Amsterdam/'
    :param alto_zip_file_path:
    :return:
    """
    alto_zip_file_path_tmp = os.path.normpath(alto_zip_file_path)
    alto_zip_file_name = os.path.basename(alto_zip_file_path_tmp)

    edm_xml_file_name = alto_zip_file_name.replace("alto.zip", "edm.xml")
    edm_xml_file_path = alto_zip_file_path_tmp.replace(alto_zip_file_name, edm_xml_file_name)
    if not os.path.isfile(edm_xml_file_path):
        edm_xml_file_name = edm_xml_file_name.replace('_',' ')
        edm_xml_file_path = alto_zip_file_path_tmp.replace(alto_zip_file_name, edm_xml_file_name)

    return edm_xml_file_path


def index_whole_library_newspapers(provider_dir):
    """

    :param provider_dir: data provider directory path that contains all the issues datasets
    :return: None
    """
    all_newspaper_dir = load_all_newspapers_from_provider(provider_dir)
    print("total [%s] newspapers found from library [%s]" % (len(all_newspaper_dir), provider_dir))
    for newspaper_dir in all_newspaper_dir:
        index_whole_newspaper_alto_fulltext(newspaper_dir)

    print("all newspapers are indexed from data provider [%s] " % provider_dir)
    print("total page indexed: ", total_page_indexed)
    print("total documents without fulltext or fulltext file is invalid: ", invalid_fulltext_file)
    print("total documents without edm metadata: ", fulltext_without_edm_metadata)
    print("total documents without page level language: ", fulltext_without_page_level_lang)


def index_whole_newspaper_alto_fulltext(newspaper_dir):
    """

    :param newspaper_dir: issue directory path that contains all the page fulltext datasets of an issue
    :return:
    """
    issue_all_issue_files = load_all_issues_alto_fulltext(newspaper_dir)
    print("total [%s] issues found from newspaper [%s]" % (len(issue_all_issue_files), newspaper_dir))
    for issue_fulltext_path in issue_all_issue_files:
        index_issue_page_fulltext(issue_fulltext_path)


def index_issue_page_fulltext(issue_fulltext_path):
    """

    :param page_fulltext_path: page fulltext file of an issue
    :return:
    """

    global invalid_fulltext_file
    global fulltext_without_edm_metadata
    global fulltext_without_page_level_lang
    global total_page_indexed

    parsing_err = False
    issue_fulltext_pages = []
    try:
        issue_fulltext_pages = extract_fulltext_4_issue(issue_fulltext_path)
    except zipfile.BadZipFile as badFileErr:
        # e.g., National_Library_of_Estonia\Postimees\1897-11-06.alto.zip is invalid
        print("Failed to index current issue [%s] !!! Error: %s " % (issue_fulltext_path, badFileErr))
        invalid_fulltext_file += 1
        parsing_err = True

    if parsing_err:
        return

    print("total [%s] pages loaded for issue [%s]" %(len(issue_fulltext_pages), issue_fulltext_path))

    bb_resource = load_edm_in_xml(_get_edm_xml_file(issue_fulltext_path))

    if bb_resource is None:
        # raise Exception("no edm metadata found for issue [%s]" % issue_fulltext_path)
        # e.g., National_Library_of_Latvia/Goriga_Maize._%22Drywas%22_pilykums/ do not have issue level metadata
        # e.g., National_Library_of_the_Netherlands/De_grondwet/1860-1940_%3F_.alto.zip
        print("Warning: no edm metadata found for issue [%s]" % issue_fulltext_path)
        bb_resource = BibliographicResource()
        bb_resource.issue_id = os.path.basename(issue_fulltext_path).replace(".alto.zip", "")
        fulltext_without_edm_metadata += 1

    bb_resource_dict = bb_resource.to_dict()
    issue_id = bb_resource_dict['issue_id']
    bb_resource_dict.pop('issue_id')
    solr_docs = []
    for issue_fulltext_page in issue_fulltext_pages:
        if (issue_fulltext_page.language is None or issue_fulltext_page.language == '') \
                and 'proxy_dc_language' in bb_resource_dict:
            # language is not available in National_Library_of_the_Netherlands alto file dataset
            # we use the language in issue level edm metadata temporarily instead if it is available
            #   set page level language with issue level page
            issue_fulltext_page.language = bb_resource_dict["proxy_dc_language"][0]
            fulltext_without_page_level_lang += 1

        # combine page fulltext with metadata into every individual Solr doc
        solr_doc = {**issue_fulltext_page.to_edm_json(), **bb_resource_dict}
        # set document id as a combination of issue id and page no
        solr_doc['europeana_id'] = issue_id + "_" + str(issue_fulltext_page.page_no)
        #todo good to have an indexing time field
        solr_docs.append(solr_doc)

    print("total [%s] solr document size to be indexed for issue [%s]: " % (len(solr_docs), issue_fulltext_path))

    # print(solr_docs)
    total_page_indexed += len(solr_docs)
    response = solrClient.batch_update_documents(solr_docs)
    print("indexing done. status: ", response)

    print(">>>>>>>>>>>>>>>>>>>>>>>")


def index_all_edm_fulltext_datasets(edm_dir):
    """
    load all edm fulltext zipped datasets
    :param edm_dir: directory containing all fulltext edm datasets
    :return: list, edm zipped datasets
    """
    all_fulltext_edm_dataset = load_files_path_from_dir(edm_dir)


def index_fulltext_edm_dataset(solr_collection_uri, zipped_dataset_path, cpu_cores=1):
    print("indexing Fulltext EDM dataset %s ..." % zipped_dataset_path)

    all_fulltext_edm_files = load_all_files_from_zip_file(zipped_dataset_path)

    if cpu_cores > 1:
        parallel_bulk_indexing_fulltext_edm_dataset(all_fulltext_edm_files, cpu_cores, solr_collection_uri)
    else:
        batch_bulk_indexing_fulltext_edm_dataset(all_fulltext_edm_files, solr_collection_uri)

    print("all complete.")


def batch_bulk_indexing_fulltext_edm_dataset(all_fulltext_edm_files, solr_collection_uri):
    index_batch_num = 100
    solr_docs = []
    solr_client = SolrClient(solr_collection_uri)
    progress = 0
    for fulltext_edm_file_content, file_name, total_files_size in all_fulltext_edm_files:
        fulltext_edm_model = extract_edm_fulltext_model(fulltext_edm_file_content, file_name)
        try:
            solr_docs.append(fulltext_edm_model.to_edm_json())
            if len(solr_docs) == index_batch_num:
                response = solr_client.batch_update_documents(solr_docs)
                print("indexing current batch done. status: ", response)
                progress += index_batch_num
                print("progress: %s (%s/%s) " % (float(progress / total_files_size), progress, total_files_size))
                solr_docs.clear()
        except SolrError as err:
            print("Indexing error", str(err))
            print("doc: ", fulltext_edm_model.to_json())
            break
    if len(solr_docs) > 0:
        print("submitting remaining [%s] documents" % len(solr_docs))
        try:
            response = solr_client.batch_update_documents(solr_docs)
            print("indexing current batch done. status: ", response)
        except SolrError as err:
            print("Indexing error", str(err))


def parallel_bulk_indexing_fulltext_edm_dataset(all_fulltext_edm_files, cpu_cores, solr_collection_uri):
    """
    Warning: Experimental method and need more test

    :param all_fulltext_edm_files:
    :param cpu_cores:
    :param solr_collection_uri:
    :return:
    """
    print("cpu cores: ", cpu_cores)
    with Pool(processes=cpu_cores) as pool:
        pool.starmap(_index_edm_fulltext_content, zip(all_fulltext_edm_files, repeat(solr_collection_uri)),
                     chunksize=200)


# fulltext_edm_file_content, file_name, total_files_size,
def _index_edm_fulltext_content(edm_file_data, solr_server_uri):
    fulltext_edm_file_content, file_name, total_files_size = edm_file_data
    fulltext_edm_model = extract_edm_fulltext_model(fulltext_edm_file_content, file_name)
    solr_client = SolrClient(solr_server_uri)
    try:
        solr_client.batch_update_documents([fulltext_edm_model.to_edm_json()])
    except SolrError as err:
        print("Indexing error", str(err))
        print("doc: ", fulltext_edm_model.to_json())
    """
    docs_buffer = bulkDocUpdateCache.add_new(fulltext_edm_model.to_edm_json())
    if len(docs_buffer) == index_batch_num:
        progress = bulkDocUpdateCache.value
        print("progress: %s (%s/%s)" % (float(progress/total_files_size), progress, total_files_size))
        solr_client = SolrClient(solr_server_uri)
        try:
            solr_client.batch_update_documents(docs_buffer)
        except SolrError as err:
            print("Indexing error", str(err))
            print("doc: ", fulltext_edm_model.to_json())

        bulkDocUpdateCache.clean_top_n(index_batch_num)
    """


def index_metadata_edm_dataset(solr_collection_uri, zipped_dataset_path):
    print("indexing Metadata EDM dataset %s ..." % zipped_dataset_path)

    all_metadata_edm_files = load_all_files_from_zip_file(zipped_dataset_path)

    dataset_id = extract_file_name(zipped_dataset_path, extension=".zip")
    index_batch_num = 10
    solr_docs = []
    solr_client = SolrClient(solr_collection_uri)
    progress = 0

    for metadata_edm_file_content, file_name, total_files_size in all_metadata_edm_files:
        bb_resource = extract_edm_metadata_model(metadata_edm_file_content)
        bb_resource.set_europeana_id(dataset_id)
        try:
            solr_docs.append(bb_resource.to_dict())
            if len(solr_docs) == index_batch_num:
                response = solr_client.batch_update_documents(solr_docs)
                print("indexing current batch done. status: ", response)
                print("progress: ", float(progress/total_files_size))
                progress += index_batch_num
                solr_docs.clear()
        except SolrError as err:
            print("Indexing error", str(err))
            print("doc: ", bb_resource.to_json())
            print("doc: ", file_name)
            break
    print("all complete.")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        solr_server_uri = str(sys.argv[1])
        dataset_type = str(sys.argv[2])
        index_target = str(sys.argv[3])
        cpu_cores = 1
        if len(sys.argv) == 5:
            cpu_cores = int(sys.argv[4])

        print("indexing [%s] into [%s] ... " % (index_target, solr_server_uri))
        if dataset_type == "fulltext":
            print("indexing the EDM fulltext dataset ...")
            import time
            start_time = time.time()
            index_fulltext_edm_dataset(solr_server_uri, index_target, cpu_cores=cpu_cores)
            print("--- %s seconds ---" % (time.time() - start_time))
        elif dataset_type == "metadata":
            print("indexing with EDM metadata dataset ...")
            import time
            start_time = time.time()
            index_metadata_edm_dataset(solr_server_uri, index_target)
            print("--- %s seconds ---" % (time.time() - start_time))

    else:
        # ("metadata"| "fulltext")
        print("python newspaper_dumps_reader.py <solr_server_url> <dataset_type> <newspaper_library_directory> <CPU_CORES>")


