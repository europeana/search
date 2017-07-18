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

        # populating the fields drop down
        # TODO: maybe reverse this, owing to frequency of
        # copyfield use?
        self.fields["query_transmitter"] = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={ "type" : "hidden"}))
        self.fields["reset_form"] = forms.CharField(max_length=1, initial="F", widget=forms.TextInput(attrs={ "type" : "hidden"}))
        self.fields["search_id"] = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "search_as_url"}))
        self.fields["search_as_query"] = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={ "type" : "hidden", "id": "search_as_query" }))
        self.fields["page"] = forms.CharField(max_length=2, initial="1", widget=forms.TextInput(attrs={ "type" : "hidden", "id" : "page_no"}))
        fields = [('', '----------')]
        for row in CandidateField.objects.all().order_by('field_name'):
            fields.append((row.field_name, row.field_name))

        # first, need to be able to pick out the entity
        self.fields["picked_entity"] = forms.CharField(label='Entity', max_length=250, required=True, widget=forms.Textarea(attrs={ 'class' : 'entity-picked ', 'rows' : 4 }))

        for i in range(4):
            self.create_clause_group(i, fields)
            for j in range(4):
                pos = str(i) + "_" + str(j)
                self.create_clause_group(pos, fields)

    def create_clause_group(self, position, fields):
        subprefix = ""
        if("_" in str(position)):
            subprefix = "sub"
            (clause_number, subclause_number) = position.split("_")
            clause_number = int(clause_number) + 1
            subclause_number = int(subclause_number) + 1
            lbl = "Clause " + str(clause_number) + ", subclause " + str(subclause_number)
            self.fields['subclause_' + position + "_activator"]  = forms.BooleanField(label=lbl, required=False, widget=forms.CheckboxInput(attrs={ 'class' : 'activator'}))
        else:
            is_checked = int(position) == 0
            label="Clause " + str(position + 1)
            if(position == 0): label += " (mandatory)"
            self.fields['clause_' + str(position) + '_activator'] = forms.BooleanField(label=label, required=False, initial=is_checked, widget=forms.CheckboxInput(attrs={ 'class' : 'activator'}))
        # (i)   Operator picker (AND|OR)
        self.fields[subprefix + 'clause_' + str(position) + '_operator'] = forms.ChoiceField(label="Operator", choices=[('AND', 'AND'), ('OR', 'OR')], initial='AND', required=False, widget=forms.RadioSelect(attrs={ 'class' : subprefix + 'clause-operator'}))
        # (ii)  Field selector
        self.fields[subprefix + 'clause_' + str(position) + '_field'] = forms.ChoiceField(label="Field Name", choices=fields, initial='', required=(position == 0), widget=forms.Select(attrs={ 'class' : subprefix + 'clause-field'}))
        # (iii) URL or term input 
        self.fields[subprefix + 'clause_' + str(position) + '_mode'] = forms.ChoiceField(label="Mode", choices=[('URL', 'URL'), ('Freetext', 'Freetext')], initial='URL', required=False, widget=forms.RadioSelect(attrs={ 'class' : subprefix + 'clause-mode mode-value'}))
        # (iv)  Four subclause units (identical to the above)
        self.fields[subprefix + 'clause_' + str(position) + '_value'] = forms.CharField(label="Value", max_length=250, required=(position==0), widget=forms.TextInput(attrs={ 'class' : subprefix + 'clause-value search-terms'}))


def index(request):
    if request.method == 'POST':
        ecq = ECQueryForm(request.POST)
        if(ecq.is_valid()):
            do_reset = ecq.cleaned_data["reset_form"]
            page_no = int(ecq.cleaned_data["page"])
            if(do_reset == "T"):
                ecq = ECQueryForm()
                return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq })
            qry = ecq.cleaned_data["query_transmitter"]
            results = do_basic_query(qry, page_no)
            page_range = get_page_range(page_no, results)
            page_info = generate_page_info(page_no, results)
            try:
                results = results['response']
            except KeyError: # in this case the response from the server is bad
                pass
            return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq, 'query' : qry, 'results': results, 'page_number' : page_no,  'page_range' : page_range, 'page_info' : page_info })
    else:
        ecq = ECQueryForm()
    return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq })

def do_basic_query(query_string, page_no):
    offset = (page_no - 1) * ITEMS_PER_PAGE
    solr_url = "http://sol7.eanadev.org:9191/solr/search_2/search"
    solr_qry = solr_url + "?q=" + query_string + "&wt=json&rows=" + str(ITEMS_PER_PAGE) + "&start=" + str(offset)
    print(solr_qry)
    res = requests.get(solr_qry)
    return res.json()

def get_page_range(page_no, results):
    try:
        total_results = int(results['response']['numFound'])
    except KeyError:
        total_results = 0
    last_page_no = int(total_results) // int(ITEMS_PER_PAGE) + 1
    print(str(int(total_results) % int(ITEMS_PER_PAGE)))
    if(int(total_results) % int(ITEMS_PER_PAGE) != 0):
        last_page_no += 1
    if(last_page_no > 80):
        last_page_no = 81
    raw_pge_rng = [i for i in range(1, last_page_no)]
    pge_rng = []
    if(last_page_no >= 20):
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

def instructions(request):
    return render(request, 'rankfiddle/instructions.html')
