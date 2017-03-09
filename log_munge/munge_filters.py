# desired outputs:
# ranked list of most popular filters
# 1. absolutely
# 2. by API key
# ranked list of most popular facets
# 1. absolutely
# 2. by API key
# ranked list of combined facets + filters

EUROPEANA_KEYS = ['api2demo', 'pbPjb6xtT', 'RbWPAapQ6', 'phVKTQ8g9F', 'SQkKyghXb']

import os

def process_filters(log_dir):
    cwd = os.getcwd()
    path = os.path.join(cwd, 'output', 'logs', log_dir)
    filters_by_api = {}
    for f in os.listdir(path):
        with open(os.path.join(path, f), 'r') as filter_log:
            current_key = ""
            for line in filter_log:
                if(line.startswith('Key')):
                    linebits = line.split(':')
                    api_key = linebits[1].split("\t")[0].strip()
                    api_count = linebits[2].strip()
                    current_key = api_key
                    try:
                        filters_by_api[api_key]["count"] += int(api_count)
                    except KeyError:
                        filters_by_api[api_key] = {}
                        filters_by_api[api_key]["count"] = int(api_count)
                elif(line.strip() == ""):
                    pass
                else:
                    line = line.split("\t")
                    filter_name = line[1].strip()
                    filter_count = int(line[2].strip())
                    try:
                        filters_by_api[current_key][filter_name] += filter_count
                    except KeyError:
                        filters_by_api[current_key][filter_name] = filter_count
    return filters_by_api

def output_filter_stats(filter_type, key_type, filtermap):
    statsmap = {}
    for k, v in filtermap.items():
        if(key_type == "internal" and k in EUROPEANA_KEYS): statsmap[k] = v
        elif(key_type == "external" and k not in EUROPEANA_KEYS): statsmap[k] = v
        else: pass
    filename = filter_type + "_totals_" + key_type + ".txt"
    with open(filename, 'w') as extfac:
        for k in sorted(statsmap, key=lambda l: statsmap[l]["count"], reverse=True):
            extfac.write("Key value: " + k + "\t" + "Total requests: " + str(statsmap[k]["count"]) + "\n")
            filters_only = statsmap[k]
            for m in sorted(filters_only, key=filters_only.__getitem__, reverse=True):
                if(m != "count"):
                    extfac.write("\t" + m + ": " + str(statsmap[k][m]) + "\n")

api_facets = process_filters('facets')
output_filter_stats('facet', 'external', api_facets)
output_filter_stats('facet', 'internal', api_facets)
api_filters = process_filters('filters')
output_filter_stats('filter', 'external', api_filters)
output_filter_stats('filter', 'internal', api_filters)

combined_totals = {}

for k, v in api_facets.items():
    for field, fieldcount in v.items():
        try:
            combined_totals[field] += fieldcount
        except KeyError:
            combined_totals[field] = fieldcount

for k, v in api_filters.items():
    for field, fieldcount in v.items():
        try:
            combined_totals[field] += fieldcount
        except KeyError:
            combined_totals[field] = fieldcount

with open('combined_totals.txt', 'w') as combined:
    for field in sorted(combined_totals, key=combined_totals.__getitem__, reverse=True):
        combined.write(field  + ": " + str(combined_totals[field]) + "\n")
