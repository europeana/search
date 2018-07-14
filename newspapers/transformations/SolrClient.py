import json
import re

from urllib.parse import urlencode
from urllib.parse import urljoin, urlsplit

from httplib2 import Http
from requests.adapters import HTTPAdapter
import requests
import requests.exceptions

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=10))
s.mount('https://', HTTPAdapter(max_retries=10))
# sleep for every field analysis request to avoid "Max retries exceeded with url"
sleep_seconds_before_field_analysis_request = 0.1
from time import sleep


ER_RE = re.compile ('<pre>(.|\n)*?</pre>')

class Results(object):
    def __init__(self, response=None, decoder=None):
        self.decoder = decoder or json.JSONDecoder()
        if not response:
            self.result = {}
        else:
            self.result = self.decoder.decode(response)

        self.highlighting = {}
        self.facets = {}
        self.spellcheck = {}
        self.matches = {}
        self.interesting_terms = {}
        self.response = response

        if self.result.get('highlighting'):  # highlighting
            self.highlighting = self.result['highlighting']

        if self.result.get('facet_counts'):
            self.facets = self.result['facet_counts']

        if self.result.get('spellcheck'):
            self.spellcheck = self.result['spellcheck']

        if self.result.get('interestingTerms'):
            self.interesting_terms = self.result["interestingTerms"]

        if self.result.get('match', {}).get('docs'):
            self.matches = self.result['match']['docs']

        response = self.result.get('response')
        if response:
            self.docs = response['docs']
            self.hits = response['numFound']
        else:
            self.docs, self.hits = ([], 0)

    def __len__(self):
        return len(self.docs)

    def __iter__(self):
        return iter(self.docs)


class GroupedResults(object):
    def __init__(self, response=None, decoder=None):
        self.decoder = decoder or json.JSONDecoder()
        self.result = self.decoder.decode(response)

        grouped_response = self.result.get('grouped')
        docs = {}
        for name, res in grouped_response.iteritems():
            r = Results()
            r.docs = res.get('doclist', {}).get('docs')
            r.hits = res.get('doclist', {}).get('numFound')
            docs[name] = r

        self.docs = docs

    def __iter__(self):
        return iter(self.docs)


class SolrError(Exception):
    pass


class SolrClient(object):
    """
    Solr client APIs
    """

    solrURL = "http://144.76.218.178:9192/solr/fulltext"

    def __init__(self, server_url, decoder=None, timeout=60, result_class=Results, use_cache=None, cache=None,
                 username=None, password=None):
        # self._logger=logging.getLogger(__name__)

        self.decoder = decoder or json.JSONDecoder()
        self.solrURL = server_url
        self.scheme, netloc, path, query, fragment = urlsplit(server_url)
        netloc = netloc.split(':')

        self.host = netloc[0]
        if len(netloc) == 1:
            self.host, self.port = netloc[0], None
        else:
            self.host, self.port = netloc

        self.path = path.rstrip('/')

        self.solr_core = self.path.split('/')[-1:][0]

        self.timeout = timeout
        self.result_class = result_class

        if use_cache:
            self.http = Http(cache=cache or ".cache", timeout=self.timeout)
        else:
            self.http = Http(timeout=self.timeout)

        self._auth = None
        if username is not None and password is not None:
            # self.http.credentials.add(username,password)
            self._auth = (username, password)

    def load_documents(self, start=0, rows=10):
        """
        load/fetch indexed documents (& stored metadata) in a range (start, rows)
        start: $page_number
        rows: $rows_per_page

        return documents {'docs'[],'numFound','start' }
        """
        params = {'q': '*:*', 'start': start, 'rows': rows}
        params['wt'] = 'json'  # specify json encoding of results
        path = '%s/select?%s' % (self.path, urlencode(params, True))

        response = self._send_request('GET', path)

        return response['response']

    def batch_update_documents(self, docs, commit=True):
        """
        batch update documents

        docs: document object set in dict json format
        """

        docs = json.dumps(docs, ensure_ascii=False).encode(encoding='utf_8')

        params={'commit':'true' if commit else 'false'}
        val_headers= {"Content-type": "application/json"}
        path = '%s/update/json?%s' % (self.path, urlencode(params, True))

        response = self._send_request('POST', path, data=docs, headers=val_headers)

        '''
        import pysolr
        solr = pysolr.Solr(self.solrURL, timeout=10)
        response = solr.add(docs, commit=commit)
        '''
        #{'responseHeader': {'status': 0, 'QTime': 115}}
        return response

    def load_documents_by_custom_query(self, query_condition, start=0, rows=10):
        """
        load documents by specific query condition
        :param query_condition: solr query condition '*:*'
        :param start:
        :param rows:
        :return: solr response
        """
        params = {'q': query_condition, 'start':start, 'rows':rows}
        params['wt'] = 'json' # specify json encoding of results
        path = '%s/select?%s' % (self.path, urlencode(params, True))

        response = self._send_request('GET', path)

        return response['response']

    def load_document_by_id(self, doc_url):
        id_query="id:\"%s\""%doc_url

        results = self.load_documents_by_custom_query(id_query)
        num_found=results['numFound']
        if num_found < 1:
            return None

        docs = results['docs']

        return docs[0]

    def total_document_size(self):
        result = self.load_documents(rows=0)
        return result['numFound']


    def _send_request(self, method, path, data=None, headers=None, sleep_before_request=0):
        """
        :param method: HTTP method include 'GET','POST','DELETE','PUT'
        :param path: request url path,
        :param path: data to send with the request
        :param path: headers information
        :param sleep_before_request: sleep(timeinsec) to allow enough time gap to send requests to server
                            this is to avoid ConnectionError "Max retries exceeded with url". Default with no delay
        :return: response in json format
        """

        url = self.solrURL.replace(self.path, '')
        sleep(sleep_before_request)
        try:
            if self._auth:
                response = requests.request(method=method, url=urljoin(url, path),
                                            headers=headers,data=data,auth=self._auth)
            else:
                response = requests.request(method=method, url=urljoin(url, path),
                                            headers=headers,data=data)
        except requests.exceptions.ConnectionError:
            # self._logger.warning("Connection refused when requesting [%s]", urljoin(url, path))
            raise SolrError("Connection refused.")

        if response.status_code not in (200, 304):
            # self._logger.error("failed to send request to [%s]. Reason: [%s]", urljoin(url, path),response.reason)
            print("failed to send request to [%s]. Reason: [%s]" % (urljoin(url, path),response.reason))
            raise SolrError(self._extract_error(headers, response.reason))

        return response.json()

    def _extract_error(self, headers, response):
        """
        Extract the actual error message from a solr response. Unfortunately,
        this means scraping the html.
        """
        reason = ER_RE.search(response)
        if reason:
            reason = reason.group()
            reason = reason.replace('<pre>','')
            reason = reason.replace('</pre>','')
            return "Error: %s" % str(reason)
        return "Error: %s" % response