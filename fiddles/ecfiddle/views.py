from django.shortcuts import render
from django import forms
from .models import CandidateField
from django.http import HttpResponse, JsonResponse
import requests
import json

class ECQueryForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        # populating the fields drop down
        # TODO: maybe reverse this, owing to frequency of
        # copyfield use?
        self.fields["query_transmitter"] = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={ "type" : "hidden"}))
        fields = [('', '----------')]
        for row in CandidateField.objects.all().order_by('field_name'):
            fields.append((row.field_name, row.field_name))

        # first, need to be able to pick out the entity
        self.fields["picked_entity"] = forms.CharField(label='Entity', max_length=250, widget=forms.TextInput(attrs={ 'class' : 'entity-picked '}))

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
        self.fields[subprefix + 'clause_' + str(position) + '_field'] = forms.ChoiceField(label="Field Name", choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : subprefix + 'clause-field'}))
        # (iii) URL or term input 
        self.fields[subprefix + 'clause_' + str(position) + '_mode'] = forms.ChoiceField(label="Mode", choices=[('URL', 'URL'), ('Freetext', 'Freetext')], initial='URL', required=False, widget=forms.RadioSelect(attrs={ 'class' : subprefix + 'clause-mode mode-value'}))
        # (iv)  Four subclause units (identical to the above)
        self.fields[subprefix + 'clause_' + str(position) + '_value'] = forms.CharField(label="Value", max_length=250, required=False, widget=forms.TextInput(attrs={ 'class' : subprefix + 'clause-value search-terms'}))


def index(request):
    if request.method == 'POST':
        ecq = ECQueryForm(request.POST)
        if(ecq.is_valid()):
            qry = ecq.cleaned_data["query_transmitter"]
            results = do_basic_query(qry)
            try:
                results = results['response']
            except KeyError: # in this case the response from the server is bad
                pass
            return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq, 'query' : qry, 'results': results})
    else:
        ecq = ECQueryForm()
    return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq })

def do_basic_query(query_string):
    solr_url = "http://sol7.eanadev.org:9191/solr/search_2/search"
    solr_qry = solr_url + "?q=" + query_string + "&wt=json"
    res = requests.get(solr_qry)
    return res.json()

def instructions(request):
    return render(request, 'rankfiddle/instructions.html')
