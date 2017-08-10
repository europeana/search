import os, datetime, json, re
from socket import timeout
from . import ES_URL, EMPTY_FIELD_MSG, util
from .util import UnknownInteraction as uninter
from .util import RankedRetrieveRecordInteraction as rrinter
from .util import SearchInteraction as ssinter
from .util import ArbitraryAccessInteraction as aainter
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match
from elasticsearch_dsl.connections import connections

ES_INSTANCE = connections.create_connection(hosts=[ES_URL], timeout=60)

class EntryExtractor:

    def __init__(self, start_date, end_date, verbose=True):
        self.start_date_as_string = start_date
        self.end_date_as_string = end_date
        self.start_date = util.create_date_object(start_date)
        self.end_date = util.create_date_object(end_date)
        self.verbose = verbose
        self.sessid_directory = os.path.join(os.path.dirname(__file__), 'intermediate_output', 'sessions') # read directory
        self.entry_directory =  os.path.join(os.path.dirname(__file__), 'intermediate_output', 'entries_by_session') # write directory
        self.temporal_filter = Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(self.start_date) + "Z",'lte': datetime.datetime.isoformat(self.end_date) + "Z"}}})
        self.create_base_search()
        self.create_mlt_search()

    def create_base_search(self):
        self.base_search = Search(using=ES_INSTANCE, index="logstash-*").query(Match(message={ "query" : "Search interaction", "type" : "phrase"})).query('bool', filter=[self.temporal_filter])

    def create_mlt_search(self):
        self.mlt_search = Search(using=ES_INSTANCE, index="logstash-*").query(Match(message={ "query" : "[200] GET", "type" : "phrase" })).query('bool', filter=[self.temporal_filter]).query('bool', filter=[~Q('terms', message=['index', 'search.json', 'ancestor-self-siblings.json'])]).query(Match(action={ "query" : "show"}))
        
    def extract_entries(self):
        scan_files = self.scan_sessions()
        if(len(scan_files) == 0):
            print("No session ID files were found for the selected dates.")
            exit()
        if(self.verbose):
            print(str(len(scan_files)) + " file(s) found for processing")
        for i in range(len(scan_files)):
            if(self.verbose): print("Processing file " + str(i + 1) + " of " + str(len(scan_files)))
            scan_file = scan_files[i]
            self.read_session_file(scan_file)
            if(self.verbose): print("Finished processing file " + str(i + 1) + " of " + str(len(scan_files)))


    def scan_sessions(self):
        # loop through the session files, checking for those with appropriate dates
        relevant_files = []
        for filename in os.listdir(self.sessid_directory):
            filebits = filename.split("TO")
            file_start = util.convert_iso_8601_date_to_int(filebits[0])
            file_end = util.convert_iso_8601_date_to_int(filebits[1].replace(".txt", ""))
            req_start = util.convert_iso_8601_date_to_int(self.start_date_as_string)
            req_end = util.convert_iso_8601_date_to_int(self.end_date_as_string)
            if(file_start <= req_end and file_end >= req_start):
                relevant_files.append(filename)
            else:
                pass
        return relevant_files

    def get_individual_session(self, sess_id, output_dir=None):
        if(output_dir is None):
            output_dir = self.entry_directory
        formatted_entries = self.query_for_session_entries(sess_id)
        self.output_session(sess_id, formatted_entries, output_dir)

    def read_session_file(self, session_file):
        with open(os.path.join(self.sessid_directory, session_file)) as sessids_scan:
            size=sum(1 for _ in sessids_scan)
        with open(os.path.join(self.sessid_directory, session_file)) as sessids:
            line_counter = 0
            for line in sessids.readlines():
                sessid = line.strip()
                session_entries = self.query_for_session_entries(sessid)
                mlt_entries = self.query_for_mlt_entries(sessid, session_entries)
                combined_entries =  self.combine_session_and_mlt_entries(session_entries, mlt_entries)
                if(len(combined_entries) > 0):
                    self.output_session(sessid, combined_entries)
                else:
                    print("Finished processing files until " + self.end_date_as_string)
                    exit()
                line_counter += 1
                if(self.verbose and line_counter % 100 == 0):
                    print("Processed " + str(line_counter) + " lines out of " + str(size) + " in file.")

    def query_for_session_entries(self, sess_id):
        sess_search = self.base_search.query(Q("match", session_id=sess_id)).sort('@timestamp')[:1000]
        try:
            r = sess_search.execute()
        except (BaseException, Exception, timeout):
            print("Fatal exception (probably a connection error) processing sesssion " + sess_id)
            exit()
        formatted_entries = []
        for hit in r.hits:
            formatted_entry = self.parse_entry(hit)
            formatted_entries.append(formatted_entry)
        return formatted_entries

    def query_for_mlt_entries(self, sess_id, searched_items):
        mlt_search = self.mlt_search.query(Q("match", session_id=sess_id)).sort('@timestamp')[:1000]
        serp_records = self.extract_serp_records(searched_items)
        all_mlts = []
        try:
            r = mlt_search.execute()
        except:
            print("Execution of MLT query failed")
            return
        for hit in r.hits:
            path = self.standardise_path(hit['path'])
            if(path not in serp_records and ".html" in hit['path']):
                parsed_mlt = self.parse_entry(hit)
                all_mlts.append(parsed_mlt)
        return all_mlts 

    def combine_session_and_mlt_entries(self, session_entries, mlt_entries):
        session_entries.extend(mlt_entries)
        combined_entries = sorted(session_entries, key=lambda x: x[0])
        return combined_entries

    def extract_serp_records(self, all_searches):
        serp_records = []
        for search in all_searches:
            if(type(search) is rrinter):
                record = self.standardise_path(search.uri)
                serp_records.append(record)
        return serp_records

    def standardise_path(self, raw_record):
        record_bits = raw_record.replace(".html", "").split("/")
        record = "/" + record_bits[-2] + "/" + record_bits[-1]
        return record

    def parse_entry(self, log_entry):
        timestamp = log_entry['@timestamp']
        msg = log_entry['message']
        session_id = log_entry['session_id']
        parsed_msg = self.parse_message(msg)
        if(len(parsed_msg) == 1 and parsed_msg[0].startswith('[200] GET')):
            return aainter(timestamp, session_id, parsed_msg[0])
        elif(len(parsed_msg) == 3):
            (q, fl, total) = parsed_msg
            return ssinter(timestamp, session_id, q, fl, total)
        elif(len(parsed_msg) == 5):
            (q, rec, fl, total, rank) = parsed_msg
            return rrinter(timestamp, session_id, q, fl, rec, rank, total)
        else:
            msg = str(parsed_msg)
            return uninter(timestamp, session_id, msg)

    def parse_message(self, msg):
        # there are two kinds of custom log records
        # (both indicated with the phrase "Search interaction")
        # 1. Initial search, yielding a SERP
        # 2. Clicking on an item in the SERP
        # we need to parse these two kinds of record
        # somewhat differently
        msg = msg.replace("\n", " ")
        if("Search interaction" not in msg):
            return [msg]
        elif(("Result rank:") not in msg):
            total = msg[msg.rindex(":") + 1:].strip()
            params = msg[msg.index('{'):msg.rindex('}') + 1]
            (query, constraints_as_json) = self.get_query_and_constraints(params)
            if(self.string_only_whitespace(query)): query = EMPTY_FIELD_MSG
            return [query, str(constraints_as_json), total]
        else:
            qbits = msg.split("Search parameters:")
            rec = qbits[0][len("Search interaction: * Record:"):qbits[0].rindex("*")].strip()
            params = qbits[1][qbits[1].index("{"):qbits[1].rindex("}") + 1]
            rank = qbits[1][qbits[1].rindex(":") + 1:].strip()
            total = qbits[1][qbits[1].index("Total hits:") + len("Total hits:"):qbits[1].rindex("*")].strip()
            (query, constraints_as_json) = self.get_query_and_constraints(params)
            if(self.string_only_whitespace(query)): query = EMPTY_FIELD_MSG
            return [query, rec, str(constraints_as_json), total, rank]

    def string_only_whitespace(self, test_string):
        return (re.sub(r"\s", "",  test_string) == "")

    def jsonify(self, as_string):
        params = as_string.replace("=>", ":")
        try:
            as_json = json.loads(params)
            return as_json
        except Exception as e:
            print("Failed to load params as JSON: " + str(e))

    def get_query_and_constraints(self, params):
        pardict = self.jsonify(params)
        try:
            query = pardict['q']
        except:
            query = ""
        try:
            constraints = pardict['f']
        except:
            constraints = ""
        return (query, constraints)

    def output_session(self, session_id, parsed_entry_list, entry_directory=None):
        if(entry_directory is None):
            entry_path = os.path.join(self.entry_directory, session_id + ".txt")
        else:
            entry_path =  os.path.join(os.path.dirname(__file__), entry_directory, session_id + ". txt") # write directory
        with open(entry_path, 'a') as sout:
            prev_entry = uninter("DUMMY TIMESTAMP", "DUMMY SESSION ID", "DUMMY MESSAGE")
            for entry in parsed_entry_list:
                base_search_type = self.determine_interaction_type(prev_entry, entry)
                msg = base_search_type + "\t" + "\t".join(entry) + "\n"
                sout.write(msg)
                prev_entry = entry

    def determine_interaction_type(self, prev_entry, now_entry):
        ptype = type(prev_entry)
        ntype = type(now_entry)
        search_type = ntype.__name__
        if(ptype == ntype and ptype == ssinter):
            sterm = now_entry.search_term
            cons = now_entry.constraints
            rco = now_entry.result_count
            psterm = prev_entry.search_term
            pcons = prev_entry.constraints
            prco = prev_entry.result_count
            if(sterm == psterm and cons == pcons and rco == prco):
                search_type = "RefreshOrPaginationInteraction"
            elif(sterm == psterm and cons == pcons and rco < prco):
                search_type = "CollectionFilterAdditionInteraction"
            elif(sterm == psterm and cons == pcons and rco > prco):
                search_type = "CollectionFilterRemovalInteraction"
        return search_type
