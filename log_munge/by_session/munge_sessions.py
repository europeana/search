# we want to eliminate duplicate entries from log files
# 'duplicate' entries are those which do not add any information to the
# previous log entry (typically, rerequests for the same page)
# Note, however, that these duplicates occur in a variety of forms
# typically, we have both a 'Search interaction' message that gives us the
# file requested, followed by a GET call requesting the same files
# browser refreshes also give us exact duplicates

from collections import namedtuple
import re, os

RemoveFilterInteract = namedtuple('RemovedFilterInteract', 'timestamp result_count')
RetrieveRecordInteract = namedtuple('RetrieveRecordInteract', 'timestamp uri')
SearchInteract = namedtuple('SearchInteract', 'timestamp search_term constraints result_count')
RankedRetrieveRecordInteract = namedtuple('RankedRetrieveRecordInteract', 'timestamp search_term constraints uri rank result_count')
MiscInteract = namedtuple('MiscInteract', 'timestamp message')
ErrorInteract = namedtuple('ErrorInteract', 'message')

def load_interactions(filepath):
    print(filepath)
    interactions = []
    with open(filepath, 'r') as interaction_list:
        for line in interaction_list.readlines():
            interactions.append(line.strip())
    return interactions

def parse_to_tuple_type(interaction):
    intbits = interaction.split("\t")
    if(len(intbits) < 1):
        return ErrorInteract("Empty line")
    timestamp = intbits[0]
    if(len(intbits)  < 2):
        return MiscInteract(timestamp, " ".join(intbits))
    elif(re.match('\[\d{3}\] GET', intbits[1])):
        uri = intbits[1].strip().split()[2]
        return RetrieveRecordInteract(timestamp, uri)
    elif(len(intbits) == 4 and intbits[1] == "" and intbits[2] == ""):
        return RemoveFilterInteract(timestamp, intbits[-1])
    elif(len(intbits) == 4):
        (_, search_term, constraints, result_count) = intbits
        return SearchInteract(timestamp, search_term, constraints, result_count)
    elif(len(intbits) == 6):
        (_, search_term, uri, constraints, result_count, rank) = intbits
        return RankedRetrieveRecordInteract(timestamp, search_term, constraints, uri, rank, result_count)
    else:
        return MiscInteract(timestamp, " ".join(intbits))

def parse_interactions(interactions):
    parsed_interactions = [parse_to_tuple_type(interaction) for interaction in interactions]
    return parsed_interactions

def interactions_are_same(inter_1, inter_2):
    if(inter_1 is None and inter_2 is None):
        return True
    if(inter_1 is None or inter_2 is None):
        return False
    t1 = type(inter_1).__name__
    t2 = type(inter_2).__name__
    if(t1 == 'RemovedFilterInteract' and t2 == 'RemovedFilterInteract'):
        if(inter_1.result_count == inter_2.result_count):
            return True
        else:
            return False
    if('uri' in inter_1._fields and 'uri' in inter_2._fields):
        if((inter_1.uri in inter_2.uri) or (inter_2.uri in inter_1.uri)):
            return True
        else:
            return False
    if(t1 == 'SearchInteract' and t2 == 'SearchInteract'):
        if(inter_1.search_term == inter_2.search_term and inter_1.constraints == inter_2.constraints and inter_1.result_count == inter_2.result_count):
            return True
        else:
            return False
    return False

def strip_out_pseudoreqs(interactions):
    stripped_interactions = []
    for interaction in interactions:
        if(type(interaction).__name__ == "RetrieveRecordInteract"):
            if(re.match('/portal/.*/search', interaction.uri)):
                continue
            else:
                stripped_interactions.append(interaction)
        else:
            stripped_interactions.append(interaction)
    return stripped_interactions

def kill_duplicates(interactions):
    cleaned_interactions = strip_out_pseudoreqs(interactions)
    trimmed_interactions = []
    prev_interaction = None
    for interaction in cleaned_interactions:
        if(interactions_are_same(prev_interaction, interaction)):
            pass
        else:
            trimmed_interactions.append(interaction)
            prev_interaction = interaction
    return trimmed_interactions

def output_interactions(filepath, interactions):
    with open(filepath, 'w') as flout:
        for i in interactions:
            msg = ""
            t = type(i).__name__
            if(t == "RemovedFilterInteract"):
                msg = i.timestamp + "\tCONSTRAINT REMOVED\tResult count:"  + i.result_count
            elif(t == "RetrieveRecordInteract"):
                msg = i.timestamp + "\tPAGE REQUESTED\t" + i.uri
            elif(t == "RankedRetrieveRecordInteract"):
                constraints = i.constraints
                if(constraints == ""): constraints = "NONE"
                msg = i.timestamp + "\tRANK PAGE REQUESTED\t" + i.uri + "\tSearch Term:" + i.search_term + "\tConstraints: " + constraints + "\tRank:" + str(i.rank) + "\tTotal hits:" + str(i.result_count)
            elif(t == "SearchInteract"):
                constraints = i.constraints
                if(constraints == ""): constraints = "NONE"
                msg = i.timestamp + "\tSEARCH ENTERED\tSearch terms:" + i.search_term + "\tConstraints:" + constraints + "\tResult count:" + str(i.result_count)
            elif(t == "MiscInteract"):
                msg = i.timestamp + "\tUNCLASSIFIED\t" + i.message
            else:
                msg = "ERROR: " + i.message
            msg = msg + "\n"
            flout.write(msg)

def process_file(filename):
    raw_interactions = load_interactions(filename)
    parsed_interactions = parse_interactions(raw_interactions)
    deduped_interactions = kill_duplicates(parsed_interactions)
    output_interactions("cleaned_sessions/" + filename.split("/")[-1], deduped_interactions)

cwd = os.getcwd()
path = os.path.join(cwd, 'sessions')
for f in os.listdir(path):
    process_file(os.path.join(path, f))
