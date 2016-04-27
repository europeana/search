class Indexer:
    """
    Class to send files over the wire to Solr.
    """

    # TODO: Parameterize core name

    def __init__(self, solr_url = "144.76.218.178", solr_port="8080"):
        self.solr_url = solr_url
        self.solr_port = solr_port
        self.update = "http://" + self.solr_url + ":" + self.solr_port + "/solr/search_1_shard1_replica1/update"

    def index_file(self, filepath):
        """
        Indexes a file to Solr.
        :param filepath: path to file to be indexed (string)
        :return: response status code (int)

        Note that exceptions are thrown, to be logged by the Celery task logger
        """
        import requests
        file = {'file': ( filepath, open(filepath, 'rb'), 'text/xml', {'Expires': '0'})}
        r = requests.post(self.update, files=file)
        st = r.status_code
        if(st == 400):
            raise UndefinedFieldException(r.text)
        return st

    def commit(self):
        import requests

        commit_url = self.update + "?commit=true"
        r = requests.get(commit_url)
        return r.status_code

class UndefinedFieldException(Exception):
    """
    Custom exception class which extracts the error message
    from Solr's XML error response
    """
    # TODO: add in file name as well as field name

    def __init__(self, raw_solr_msg):
        import xml.etree.ElementTree as ET
        doc = ET.fromstring(raw_solr_msg)
        err_msg = doc.find('.//str[1]').text
        Exception.__init__(self, err_msg)



