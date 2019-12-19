import requests
import re
import urllib

# first, we need to get the current ranking of the results

outdir = "current_logs"
indir = "old_logs"
solr_prod = 'http://sol3.eanadev.org:9191/solr/search_1/search'
solr_bm25f = 'http://sol7.eanadev.org:9191/solr/search/search'

def build_query_suffix(logline):
    (query, item_id, rank, total, lang, raw_filters) = logline.split("\t")
    # for some reason we've got an extraneous 'query' param at the end of some ids
    item_id = re.sub(",.*$", "", item_id)
    lang = lang.lower()
    valid_fields = ["COMPLETENESS", "LANGUAGE", "TYPE", "PROVIDER", "COUNTRY", "text", "dc_rights", "YEAR"]
    filters = []
    if raw_filters != "[]":
        pattern = re.compile("'qf=(.*?)'")
        for param in re.findall(pattern, raw_filters):
            param = urllib.parse.unquote(param)
            field = param.split(":")[0]
            if field in valid_fields: filters.append(param)
    query_suffix = "?fl=europeana_id&rows=100&q=" + query
    if(lang != ""): query_suffix + "&fq=LANGUAGE:" + lang
    if(len(filters) > 0):
        for filter in filters:
            query_suffix += "&fq=" + filter
        return query_suffix

def get_production_ranking(query_suffix, target_id):
    # returns number of results and ranking of target_id from production solr
    query = solr_prod + query_suffix
    return get_ranking(query, target_id)

def get_bm25f_ranking(query_suffix, target_id):
    # returns number of results and ranking of target_id from test solr
    query = solr_bm25f + query_suffix
    return get_ranking(query, target_id)

def get_ranking(query, target_id):
    # given a query, performs it
    # and returns the ranking of target_id and the total number
    # of results found
    pass

def write_stats(outfile, query, item_id, rank, total, prod_25f_rank, prod_25f_total, bm25f_rank, bm_25f_total, lang, filters):
    # write comparative results to file
    # insert BM25f calculations here?
    pass


build_query_suffix("henrique de carvalho	/90101/FB4C749B285711FAEA6C352C205E2FE8CA2B4370, query=henrique de carvalho	5	7	PT	['qf=TYPE:VIDEO']")