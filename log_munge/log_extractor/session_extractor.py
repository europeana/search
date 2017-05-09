import os, datetime
from socket import timeout
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match, MultiMatch
from elasticsearch_dsl.connections import connections

ES_INSTANCE = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)

class SessionExtractor:

    def __init__(self, start_date, end_date, verbose=True):
        try:
            self.start_date = self.create_date_object(start_date)
            self.end_date = self.create_date_object(end_date)
            self.current_time = self.start_date
            self.verbose = verbose
        except ValueError as ve:
            print("Cannot parse arguments: dates must be given in the form YYYY-MM-DD")
            exit()
        filename = start_date.replace("-", "") + "TO" + end_date.replace("-", "") + ".txt"
        self.session_file = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'sessions', filename)
        if(os.path.exists(self.session_file)):
            print("A session file for that span already exists.")
            exit()
        self.session_list = []
        self.harvest_sessions()
        self.output_sessions()

    def create_date_object(self, iso_8601_date):
        # TODO: expand possible precisions - right now this automatically
        # runs midnight-to-midnight
        aug_iso_8601_date = str(iso_8601_date) +  "T00:00:00.005Z"
        date_as_obj = datetime.datetime.strptime(aug_iso_8601_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date_as_obj

    def harvest_sessions(self):
        global ES_INSTANCE
        initsearch = Search(using=ES_INSTANCE, index="logstash-*")
        session_search = initsearch.query('bool', filter=Q("exists", field="session_id"))
        bespoke_search = session_search.query(Q("match", message="Search interaction"))
        if(self.verbose): print("Starting querying for sessions")
        while(self.current_time <= self.end_date):
            next_time = self.current_time + datetime.timedelta(minutes=5)
            if(self.verbose and self.current_time.day != next_time.day):
                print("Processing " + str(datetime.datetime.isoformat(next_time).split("T")[0]))
            temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(self.current_time) + "Z",'lte': datetime.datetime.isoformat(next_time) + "Z"}}})
            temp_search = bespoke_search.query('bool', filter=[temporal_filter])
            try:
                for hit in temp_search.scan():
                    session_id = hit['session_id']
                    self.session_list.append(session_id)
            except (BaseException, Exception, timeout):
                print("Connection to ElasticSearch instance lost. Dumping contents up until " + str(datetime.datetime.isoformat(self.current_time).split("T")[0]))
                self.output_sessions()
            self.current_time = next_time
        if(self.verbose): print("Session querying complete.")

    def output_sessions(self):
        if(self.verbose): print("Outputting session IDs")
        interactions_count = len(self.session_list)
        sessions = set(self.session_list)
        sessions_count = len(sessions)
        with open(self.session_file, "w") as sout:
            sout.write(str(interactions_count) + " interactions for " + str(sessions_count) + " users.")
            for session in sessions:
                sout.write(session + "\n")
        if(self.verbose): print("Session IDs written to " + self.session_file)
        exit()
