# strips extraneous information out of 904Labs logs

import re
import os

indir = "logs"
outdir = "old_logs"
error_log = outdir + "/errors.txt"


def line_is_good(line):
    # we may want to filter out some lines as containing bot or other misleading
    # activity but for right now this is a stub
    return True

def clean_logs():
    for file in os.listdir(indir):
        if(file.startswith('trimmed')):
            infile = indir + "/" + file
            print("Processing file " + infile)
            outfile = outdir + "/" + file
            with open(infile, 'r') as dirty_logs:
                with open(outfile, 'a') as clean_logs:
                    linecount = 0
                    for line in dirty_logs:
                        if(line_is_good(line)):
                            try:
                                item_id = re.search('europeana_uri=http://www.europeana.eu/resolve/record([^s]+),', line).group(1)
                                query = re.search('query=(.+), start=', line).group(1)
                                rank = re.search('start=(.+), numFound=', line).group(1)
                                total = re.search('numFound=(.+), userId=', line).group(1)
                                lang = re.search('lang=(.+), req=', line).group(1)
                                qs = re.search('req=.+?\?(.+), date=',line).group(1)
                                boring_params = ['start', 'pageId', 'query', 'tab', 'view', 'startPage']
                                param_pairs = qs.split('&')
                                filters = []
                                for param_pair in param_pairs:
                                    try:
                                        (param, value) = param_pair.split('=')
                                        if(param not in boring_params):
                                            filters.append(param_pair)
                                    except ValueError as ve:
                                        continue
                                msg = query + "\t" + item_id + "\t" + str(rank) + "\t" + str(total) + "\t" + lang + "\t" + str(filters) + "\n"
                                clean_logs.write(msg)
                            except AttributeError as ae:
                                with open(error_log, 'a') as errs:
                                    errs.write("No match found on " + file + " line " + str(linecount) + "\n")
                                    errs.close()
                        linecount = linecount + 1

def find_qs_keys():
    qs_keys = {}
    for file in os.listdir(outdir):
        if(file != 'errors.txt'):
            linecount = 0
            filepath = outdir + "/" + file
            with open(filepath, 'r') as infile:
                for line in infile:
                    qs = line.split("\t")[5]
                    if(qs != '[]'):
                        pattern = re.compile("'(.*?)'")
                        for params in re.findall(pattern, qs):
                            try:
                                (param, value) = params.split("=")
                                if param in qs_keys:
                                    running_total = qs_keys[param][0]
                                    running_total += 1
                                    qs_keys[param][0] = running_total
                                else:
                                    qs_keys[param] = [1, value]
                            except ValueError:
                                print("Problem params detected " + file + " line " + str(linecount) + " " + params)
                                continue
                    linecount += 1
    for key, value in qs_keys.items():
        print(key + "\t" + str(value[0]) + "\t" + str(value[1]))

def find_qf_fields():
    qs_fields = {}
    for file in os.listdir(outdir):
        if(file != 'errors.txt'):
            linecount = 0
            filepath = outdir + "/" + file
            with open(filepath, 'r') as infile:
                for line in infile:
                    qs = line.split("\t")[5]
                    if(qs != '[]'):
                        pattern = re.compile("'qf=(.*?)'")
                        for params in re.findall(pattern, qs):
                            try:
                                splitval = ":" if ":" in params else "%3A"
                                (param, value) = params.split(splitval)
                                if param in qs_fields:
                                    running_total = qs_fields[param][0]
                                    running_total += 1
                                    qs_fields[param][0] = running_total
                                else:
                                    qs_fields[param] = [1, value]
                            except ValueError:
                                print("Problem params detected " + file + " line " + str(linecount) + " " + params)
                                continue
                    linecount += 1
    for key, value in qs_fields.items():
        print(key + "\t" + str(value[0]) + "\t" + str(value[1]))




find_qf_fields()
