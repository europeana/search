import json

with open ('queries_n_clicks.txt', 'r') as logs:
    qnc = json.load(logs)
    log_entries = []
    for hit in qnc["hits"]["hits"]:
        ipv4 = hit["_source"]["ipv4"]
        qry = hit["_source"]["url_query"]
        pth = hit["_source"]["origin_url_path"]
        entry = ipv4 + "\t" + qry + "\t" + pth + "\n"
        log_entries.append(entry)

with open('logs.tsv', 'w') as tablogs:
    prev_ipv4 = ""
    for entry in log_entries:
        now_ipv4 = entry.split("\t")[0]
        if(now_ipv4 != prev_ipv4): tablogs.write("----------------------\n")
        tablogs.write(entry)
        prev_ipv4 = now_ipv4
