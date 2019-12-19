import collections
import datetime
import time
import dateutil.relativedelta
import os
import re

Task = collections.namedtuple('Task', 'task_no timestamp search motive start_time end_time')

def create_date_object(datestring):
    return date_as_obj

all_tasks = {}
with open("trimmed_survey.tsv") as raw:
	for line in raw.readlines():
		try:
			(task_no, timestamp, search, motive) = line.split("\t")
			mid_t_as_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
			start_t_as_obj = mid_t_as_obj + dateutil.relativedelta.relativedelta(minutes=-30)
			end_t_as_obj = mid_t_as_obj + dateutil.relativedelta.relativedelta(minutes=+30)
			all_tasks[Task(task_no, mid_t_as_obj, search, motive, start_t_as_obj, end_t_as_obj)] = []
		except ValueError as ve:
			print("Malformed line encountered - too many tabs")

entry_directory = os.path.join(os.path.dirname(__file__), '..', 'intermediate_output', 'entries_by_session')

for filename in os.listdir(entry_directory):
	with open(os.path.join(entry_directory, filename)) as inf:
		for line in inf.readlines():
			try:
				(_, entry_timestamp, session_id, search_term, filters, _) = line.split("\t")
				entry_timestamp_as_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
				for k in all_tasks.keys():
					if(entry_timestamp_as_obj >= k.start_time and entry_timestamp_as_obj <= k.end_time):
						all_tasks[k].append((session_id, search_term))
			except ValueError as ve:
				pass # non-SearchInteraction log entries fail silently


candidate_terms_directory = os.path.join(os.path.dirname(__file__), '..', 'intermediate_output', 'candidate_terms')

for t in all_tasks.keys():
	filename = re.sub("[\W]", "", t[2])[0:25] + str(time.time()) + ".txt"
	with open(os.path.join(candidate_terms_directory, filename), "w") as tout:
		header = t[0] + "\t" + t[1].strftime("%Y-%m-%d %H:%M:%S") + "\t" + t[2] + "\t" + t[3]
		tout.write(header + "\n")
		tout.write("==================================================================\n")
		for candidate_tuple in all_tasks[t]:
			tout.write(("\t").join(candidate_tuple) + "\n")




	