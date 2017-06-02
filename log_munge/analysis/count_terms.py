import os
import re

term_counts = []
filter_counts = []

path = os.path.join(os.getcwd(), '..', 'log_extractor', 'intermediate_output', 'entries_by_session')

def count_terms(term_field):
	if(term_field == "NO VALUE PROVIDED"):
		return 0
	if(" AND " in term_field or " OR " in term_field):
		term_count = 1 + (term_field.count(" AND ") + term_field.count(" OR "))
		return term_count
	elif("(" not in term_field and ")" not in term_field):
		old_term_field = term_field
		term_field = re.sub(r":([^\"]\w+)[\s]+", r':"\1" ', term_field )
	else:
		old_term_field = term_field
		term_field = re.sub("\(", '"', term_field)
		term_field = re.sub("\)", '"', term_field)
	term_field = re.sub(r"[\w]+:", "", term_field)
	term_field = re.sub(r'\".+?\"', r'UNIT', term_field)
	term_count = term_field.count("UNIT")
	term_field = re.sub("UNIT", "", term_field)
	term_field = term_field.strip()
	if(len(term_field) > 0):
		term_count += 1
	return term_count

def count_filters(interaction_type, filters):
	filters = filters.strip()
	if(len(filters) == 0 and interaction_type == 'SearchInteraction'):
		return 0
	elif(len(filters) == 0):
		return 1
	elif(interaction_type == 'SearchInteraction'):
		return len(filters.split(":")) - 1
	else:
		return len(filters.split(":"))




for file in os.listdir(path):
	with open(os.path.join(path, file)) as sessions:
		prev_time = ""
		prev_sess = ""
		lines = []
		for line in sessions.readlines():
			if(line.startswith('SearchInteraction') or line.startswith('CollectionFilterAdditionInteraction')):
				lines.append(line)
		try:
			line = lines[-1]	
			try:
				(interaction_type, time, session_id, term, filters, count) = line.strip().split("\t")
				if(time == prev_time and session_id == prev_sess):
					pass
				else:
					term_count = count_terms(term)
					term_counts.append(term_count)
					filter_count = count_filters(interaction_type, filters)
					filter_counts.append(filter_count)
			except ValueError:
				pass
		except IndexError:
			pass

no_zeros_terms = [c for c in term_counts if c > 0]
no_zeros_filters = [c for c in filter_counts if c > 0]


term_avg = sum(no_zeros_terms) / float(len(no_zeros_terms))
filt_avg = sum(no_zeros_filters) / float(len(no_zeros_filters))


print(str(len(no_zeros_terms) / float(len(term_counts)) * 100) + " percent used a term")
print(str(len(no_zeros_filters) / float(len(term_counts)) * 100) + " percent used a filter")
print("Average number of terms used if a term was used at all: " + str(term_avg))
print("Average number of filters used if a filter was used at all: " + str(filt_avg))