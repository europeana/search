from django.shortcuts import render
from django import forms
from .models import CandidateField
from django.http import HttpResponse, JsonResponse
import requests
import json

ITEMS_PER_PAGE = 24

class ECQueryForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # first, need to be able to pick out the entity
        self.fields["solr_query"] = forms.CharField(label='Your query here', max_length=500, required=False, widget=forms.Textarea(attrs={ 'class' : 'query-to-submit', 'rows' : 6 }))
        self.fields["picked_entity"] = forms.CharField(label='Enter text to select an entity', max_length=250, required=False, widget=forms.TextInput(attrs={ 'class' : 'entity-picked '}))
        self.fields["page"] = forms.CharField(max_length=2, initial="1", widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "page_no"}))
        # persistence fields
        self.fields["entity_uri"] = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "search-as-uri" }))
        self.fields["entity_label"] = forms.CharField(max_length=350, required=False, widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "search-as-label"}))
        self.fields["do_reset"] = forms.CharField(max_length=1, initial="F", required=False, widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "do-reset" }))

def index(request):
    candidate_fields = []
    for row in CandidateField.objects.all().order_by('field_name'):
        candidate_fields.append(row.field_name)
    if request.method == 'POST':
        ecq = ECQueryForm(request.POST)
        if(ecq.is_valid()):
            if(ecq.cleaned_data["do_reset"] == "T"):
                return render(request, 'ecfiddleredux/ecfiddle.html', {'form': ECQueryForm(), 'candidate_fields':candidate_fields })
            else:
                qry = ecq.cleaned_data["solr_query"]
                page_no = int(ecq.cleaned_data["page"])
                results = do_basic_query(qry, page_no)
                page_range = get_page_range(page_no, results)
                page_info = generate_page_info(page_no, results)
                try:
                    results = results['response']
                except KeyError: # in this case the response from the server is bad
                    pass
                return render(request, 'ecfiddleredux/ecfiddle.html', {'form':ecq, 'query' : qry, 'results': results, 'page_number' : page_no,  'page_range' : page_range, 'page_info' : page_info, 'candidate_fields':candidate_fields })
    else:
        ecq = ECQueryForm()
    return render(request, 'ecfiddleredux/ecfiddle.html', {'form':ecq, 'candidate_fields':candidate_fields })

def do_basic_query(query_string, page_no):
    offset = (page_no - 1) * ITEMS_PER_PAGE
    solr_url = "http://sol7.eanadev.org:9191/solr/search_production_publish_1/search"
    solr_qry = solr_url + "?q=" + query_string + "&wt=json&rows=" + str(ITEMS_PER_PAGE) + "&start=" + str(offset)
    res = requests.get(solr_qry)
    return res.json()

def get_page_range(page_no, results):
    try:
        total_results = int(results['response']['numFound'])
    except KeyError:
        total_results = 0
    last_page_no = int(total_results) // int(ITEMS_PER_PAGE) + 1
    if(int(total_results) % int(ITEMS_PER_PAGE) != 0):
        last_page_no += 1
    if(last_page_no > 80):
        last_page_no = 81
    raw_pge_rng = [i for i in range(1, last_page_no)]
    pge_rng = raw_pge_rng
    if(last_page_no >= 20):
        pge_rng = []
        num_links = 5
        span = (num_links - 1) // 2
        if(page_no <= span):
            pge_rng = raw_pge_rng[:num_links]
            pge_rng.extend(["…"])
            pge_rng.extend([raw_pge_rng[-1]])
        elif(page_no >= raw_pge_rng[-1] - span):
            pge_rng = [raw_pge_rng[0]]
            pge_rng.extend(["…"])
            pge_rng.extend(raw_pge_rng[-num_links:])
        elif(page_no <= num_links):
            pge_rng = raw_pge_rng[:num_links + span]
            pge_rng.extend(["…"])
            pge_rng.extend([raw_pge_rng[-1]]) 
        elif(page_no >= raw_pge_rng[-1] - num_links):
            pge_rng = raw_pge_rng[:num_links]
            pge_rng.extend(["…"])
            pge_rng.extend(raw_pge_rng[-num_links - span:])           
        else:
            pge_rng = [raw_pge_rng[0]]
            pge_rng.extend(["…"])
            pge_rng.extend(raw_pge_rng[page_no - span: page_no + span])
            pge_rng.extend(["…"])
            pge_rng.extend([raw_pge_rng[-1]])
    return pge_rng

def generate_page_info(page_no, results):
    start_index = ((page_no - 1) * ITEMS_PER_PAGE) + 1
    try:
        total_items = results['response']['numFound']
        total_on_page = len(results['response']['docs']) - 1
    except KeyError:
        return "No items found"
    msg = "Items " + str(start_index) + "-" + str(start_index + total_on_page) + " of " + str(total_items)
    return msg

def reduxinstructions(request):
    return render(request, 'ecfiddleredux/instructions.html')
