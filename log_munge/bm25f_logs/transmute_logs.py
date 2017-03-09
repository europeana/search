# first pass at sucking down log data into text files

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match, Q
from elasticsearch_dsl.connections import connections
from collections import namedtuple, OrderedDict
import urllib.parse
import datetime
import json, sys, re

# we want to output APache Combined Log Format
LogEntry = namedtuple('LogEntry', 'client_ip user_id user_name timestamp request_line status_code response_size referer user_agent')
HumanReadableEntry = namedtuple('HumanReadableEntry', 'session_id timestamp query_term query_constraints item_clicked rank_position out_of')

def jsonify(as_string):
    params = as_string.replace("=>", ":")
    try:
        as_json = json.loads(params)
        return as_json
    except Exception as e:
        print("Failed to load params as JSON: " + str(e))

def get_query_and_constraints(params):
    pardict = jsonify(params)
    try:
        query = pardict['q']
    except:
        query = ""
    try:
        constraints = pardict['f']
    except:
        constraints = ""
    return (query, constraints)

def parse_message(msg):
    msg = msg.replace("\n", " ")
    qbits = msg.split("Search parameters:")
    rec = qbits[0][len("Search interaction: * Record:"):qbits[0].rindex("*")].strip()
    params = qbits[1][qbits[1].index("{"):qbits[1].rindex("}") + 1]
    rank = qbits[1][qbits[1].rindex(":") + 1:].strip()
    total = qbits[1][qbits[1].index("Total hits:") + len("Total hits:"):qbits[1].rindex("*")].strip()
    (query, constraints) = get_query_and_constraints(params)
    return (query, rec, constraints, total, rank)

def output_for_humans(session_id, entries):
    if(session_id == ""): return
    filepath = "output/for_humans/session_" + session_id + ".txt"
    with open(filepath, 'w') as sout:
        for entry in entries:
            components = [entry.timestamp, entry.query_term, str(entry.query_constraints), entry.item_clicked, entry.rank_position, entry.out_of]
            out_entry = "\t".join(components)
            out_entry = out_entry + "\n"
            sout.write(out_entry)

def output_for_machines(session_id, entries):
    if(session_id == ""): return
    filepath = "output/for_machines/session_" + session_id + ".txt"
    with open(filepath, 'w') as sout:
        for entry in entries:
            components = [entry.client_ip, entry.user_id, entry.user_name, entry.timestamp, entry.request_line, entry.status_code, entry.response_size, entry.referer, entry.user_agent]
            out_entry = "\t".join(components)
            out_entry = out_entry + "\n"
            sout.write(out_entry)

client = connections.create_connection(hosts=['http://elasticsearch2.eanadev.org:9200'], timeout=60)
basesearch = Search(using=client, index="logstash-*")
start = "2017-03-01T00:00:00.005Z"
end = "2017-03-07T00:00:00.005Z"
start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
initsearch = basesearch.query(Q("match", message='"Result rank"')).query('bool', filter=Q("exists", field="session_id")).sort('session_id', '@timestamp').query(Q({'range':{'@timestamp':{'gte': datetime.datetime.isoformat(start_date) + "Z",'lte': datetime.datetime.isoformat(end_date) + "Z"}}}))

all_for_humans = []
all_for_machines = []
session_count = 0
current_session_id = ""
for hit in initsearch.scan():
    session_id = hit['session_id']
    if(session_id != current_session_id):
        output_for_humans(current_session_id, all_for_humans)
        output_for_machines(current_session_id, all_for_machines)
        all_for_humans = []
        all_for_machines = []
        current_session_id = session_id
        session_count += 1
    timestamp = hit['@timestamp']
    msg = hit['message']
    (query, record, constraints, total, position) = parse_message(msg)
    if(constraints == ""): constraints = "-"
    for_humans = HumanReadableEntry(session_id, timestamp, query, constraints, record, position, total)
    all_for_humans.append(for_humans)
    # for the machine-readable logs we'll need to spoof some values
    user_id = "-"
    user_name = "-"
    user_agent = "\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36\""
    referer = "\"-\""
    augpath = "*" + record
    memory = "100"
    recordsearch = basesearch.query(Q("match", session_id=session_id)).query(~Q("match", message="Search interaction")).query("match", path=augpath)[0]
    trimmer = re.compile("\A(0(0)?)+")
    for hit in recordsearch.execute():
        path = hit['path']
        query = urllib.parse.quote_plus(query)
        items_per_page = 12
        page = (int(position) // items_per_page)
        rank_on_page = int(position) % items_per_page
        filters = []
        if(constraints != "-"):
            for field, values in constraints.items():
                for value in values:
                    param = field + ":" + value
                    filters.append(param)
        filtration = "&qf=".join(filters)
        if(query == ""): query = "*:*"
        page += 1
        path = path + "?page=" + str(page) + "&start=" + str(rank_on_page) + "&query=" + query
        if(len(filtration) > 0):
            path += "&qf=" + filtration
        status = hit['status']
        LogEntry = namedtuple('LogEntry', 'client_ip user_id user_name timestamp request_line status_code response_size referer user_agent')
        raw_ip = (12 - len(str(session_count))) * "0" + str(session_count)
        dotted_quad = raw_ip[0:3] + "." + raw_ip[3:6] + "." + raw_ip[6:9] + "." + raw_ip[9:12]
        quad_bits = []
        for dq in dotted_quad.split("."):
            new_quad = trimmer.sub("", dq)
            if(len(new_quad) == 0): new_quad = "0"
            quad_bits.append(new_quad)
        fixed_quad = ".".join(quad_bits)
        request_line = "\"GET " + path + " HTTP/1.0\""
        new_timestamp = "[" + datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%b/%Y:%H:%M:%S") + " +0200]"
        log_entry = LogEntry(fixed_quad, user_id, user_name, new_timestamp, request_line, str(status), memory, referer, user_agent)
        all_for_machines.append(log_entry)

output_for_humans(current_session_id, all_for_humans)
output_for_machines(current_session_id, all_for_machines)
