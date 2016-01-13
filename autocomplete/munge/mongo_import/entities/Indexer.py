class Indexer:

    def __init__(self, solr_url = "144.76.218.178", solr_port="8080"):
        self.solr_url = solr_url
        self.solr_port = solr_port
        self.update = "http://" + self.solr_url + ":" + self.solr_port + "/solr/search_1_shard1_replica1/update"

    def index_file(self, filepath):
        import requests
        file = {'file': ( filepath, open(filepath, 'rb'), 'text/xml', {'Expires': '0'})}
        r = requests.post(self.update, files=file)
        return r.status_code

    def commit(self):
        import requests

        commit_url = self.update + "?commit=true"
        r = requests.get(commit_url)
        return r.status_code



