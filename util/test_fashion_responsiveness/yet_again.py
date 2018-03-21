import requests
import json
import time

SOLR_URI = "http://sol1.eanadev.org:9191/solr/search_1/search?fq=PROVIDER:\"Europeana Fashion\"&rows=25&start=0&sort=score desc,europeana_id desc&timeAllowed=30000&f.cc_skos_prefLabel.en.facet.limit=25&fl=europeana_id timestamp_created timestamp_update timestamp PROVIDER provider_aggregation_edm_dataProvider provider_aggregation_edm_object COMPLETENESS TYPE LANGUAGE YEAR RIGHTS title proxy_dc_creator proxy_dc_contributor proxy_dc_language edm_place pl_skos_prefLabel pl_skos_prefLabel.* pl_wgs84_pos_lat pl_wgs84_pos_long edm_timespan ts_skos_prefLabel ts_skos_prefLabel.* ts_edm_begin ts_edm_end edm_agent ag_skos_prefLabel ag_skos_prefLabel.* proxy_dcterms_hasPart proxy_dcterms_spatial europeana_aggregation_edm_preview proxy_dc_title description score provider_aggregation_edm_isShownAt edm_previewNoDistribute proxy_dc_title.* proxy_dc_creator.* proxy_dc_contributor.* proxy_dc_language.* skos_concept cc_skos_prefLabel cc_skos_prefLabel.* cc_skos_broader cc_skos_broader.* ts_dcterms_isPartOf ts_dcterms_isPartOf europeana_recordHashFirstSix UGC COMPLETENESS COUNTRY europeana_collectionName pl_dcterms_isPartOf pl_skos_altLabel pl_skos_altLabel.* pl_dcterms_isPartOf timestamp_created timestamp_update&f.proxy_dc_format.en.facet.limit=25&facet.mincount=1&f.CREATOR.facet.limit=25&facet=true&facet.field=proxy_dc_format.en&facet.field=CREATOR&facet.field=cc_skos_prefLabel.en&facet.limit=25&wt=json&facet.threads=2"


terms = ["Tordoir ","Lauren","Guardian","Ferragamo","Tholance ","Joosse","Lanvin ","Akris ","Mabille "]
#"Altuzarra ","Aquilano","Erdem ","Gelderen ","Giles  ","Gucci ","Givenchy ","Jill Stuart ","Moschino ","Pilotto ","Wauchob","Theyskens","Vanessa Bruno","Westwood ","Anaya-Lucca","Balenciaga ","Burberry Prorsum ","Rucci ","Chanel  ","Ribeiro ","Coco Chanel","DKNY ","Ungaro ","Pucci ","Fashion Network","Felipe Oliveira Baptista ","Armani ","Honor ","Anderson ","Loewe ","Vuitton  ","Goldin ","Vincenzo ","Katrantzou ","Paul Joe  ","Lourenco  ","Preen ","Rebecca Taylor ","Mouret ","Sacai ","Saunders Enterprises","Temperley ","Mugler ","Ungaro","fashion collection","fashion photograph","womenswear","menswear","webpage","article","beige","tied shoes","brown","black","dress","silk","women's costume","artificial fibres","book","cocktail dress","ensemble","silver","wool","cotton","evening wear","haute couture","jacket","metal","paper","skirt","white","bag ","blouse","booties ","cardigan","costume accessories","ear ornament","evening gown","film","gold","grey","leather","print","resin","shirt","suede","vest","Color: beige","Color: brown","Color: black"]
roundtrips = []

def do_timing(term):

    term = term.strip()
    qry = SOLR_URI
    if(term == ""):
        qry += "&q=*:*"
    else:
        qry += "&q=*:*&fq=\"" + term + "\""
    #print(qry)
    start = time.time()
    full_req = requests.get(qry)
    full_req.content
    roundtrip = time.time() - start
    roundtrips.append(roundtrip)
    if(term == ""): term = "No term provided"
    numfound = full_req.json()['response']['numFound']
    print(term + "(" + str(numfound) +  "):\t\t\t\t" + str(roundtrip) + "s")

for i in range(3):
    print("ITERATION " + str(i))
    print("=============")
    do_timing("")
    for term in terms:
        do_timing(term)

    avg = float(sum(roundtrips) / len(roundtrips))
    print("\n")
    print("Avg. time taken: " + str(avg) )
    print("\n\n")
