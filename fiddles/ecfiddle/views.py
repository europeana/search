from django.shortcuts import render
from django import forms
from .models import CandidateField
from django.http import HttpResponse, JsonResponse
import requests
import json

SOLR_SHARD_EDSMX = 'http://sol1.eanadev.org:9191/solr/search_1/search'
SOLR_SHARD_NOW8T = 'http://sol3.eanadev.org:9191/solr/search_1/search'
SOLR_SHARD_TEST = 'http://sol7.eanadev.org:9191/solr/search/search'

class ECQueryForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        # populating the fields drop down
        # TODO: maybe reverse this, owing to frequency of
        # copyfield use?
        fields = [('', '----------')]
        for row in CandidateField.objects.all().order_by('field_name'):
            fields.append((row.field_name, row.field_name))

        # first, need to be able to pick out the entity
        picked_entity = forms.CharField(label='Entity', max_length=250)

        for i in range(4):
            self.create_clause_group(i, fields)
            for j in range(4):
                pos = str(i) + "_" + str(j)
                self.create_clause_group(pos, fields)

    def create_clause_group(self, position, fields):
        # (i)   Operator picker (AND|OR)
        self.fields['clause_' + str(position) + '_operator'] = forms.ChoiceField(label="Operator", choices=[('AND', 'AND'), ('OR', 'OR')], initial='AND', required=False, widget=forms.RadioSelect())
        # (ii)  Field selector
        self.fields['clause_' + str(position) + '_field'] = forms.ChoiceField(label="Field Name", choices=fields, initial='', required=False)
        # (iii) URL or term input 
        self.fields['clause_' + str(position) + '_mode'] = forms.ChoiceField(label="Mode", choices=[('URL', 'URL'), ('Freetext', 'Freetext')], initial='URL', required=False, widget=forms.RadioSelect())
        # (iv)  Four subclause units (identical to the above)
        self.fields['clause_' + str(position) + '_value'] = forms.CharField(label="value", max_length=250)


def index(request):

    if request.method == 'POST':
        ecq = ECQueryForm(request.POST)
        if(ecq.is_valid()):
           pass
           # return render(request, 'rankfiddle/rankfiddle.html', {'form':quf, 'params': build_params(results)})
    else:
        ecq = ECQueryForm()
    return render(request, 'ecfiddle/ecfiddle.html', {'form':ecq })

"""def build_params(raw_results):
    params = {}
    if('weighted' in raw_results):
        params['weighted'] = {}
        params['weighted']['headerparams'] = raw_results['weighted']['responseHeader']['params']
        params['weighted']['results'] = raw_results['weighted']['response']['docs']
        params['weighted']['count'] = raw_results['weighted']['response']['numFound']
    if('unweighted' in raw_results):
        params['unweighted'] = {}
        params['unweighted']['results'] = raw_results['unweighted']['response']['docs']
        params['unweighted']['count'] = raw_results['unweighted']['response']['numFound']
    if('bm25f' in raw_results):
        params['bm25f'] = {}
        params['bm25f']['results'] = raw_results['bm25f']['response']['docs']
        params['bm25f']['count'] = raw_results['bm25f']['response']['numFound']
    return params

def build_boosts(cleaned_data, field_name, max_fields=20):
    boosts = ""
    for i in range(1,max_fields):
        now_fn = field_name + "_" + str(i)
        if(cleaned_data[now_fn] != ''):
            field_boost = field_name + "_boost_" + str(i)
            boost = cleaned_data[now_fn] + "^" + str(cleaned_data[field_boost])
            boosts += boost + " "
    return boosts

def do_query(wv, q, qf, pf, ps, pf2, ps2, pf3, ps3, tibr):
    results = {}
    if('weighted' in wv):
        results['weighted'] = do_weighted_query(q, qf, pf, ps, pf2, ps2, pf3, ps3, tibr)
    if('unweighted' in wv):
        results['unweighted'] = do_unweighted_query(q)
    if('bm25f' in wv):
        results['bm25f'] = do_bm25f_query(q)
    return results

def do_weighted_query(q, qf, pf, ps, pf2, ps2, pf3, ps3, tibr):
    solr_url = SOLR_SHARD_EDSMX + "?q={!type=edismax}" + q;
    if(len(qf) > 0):solr_url += "&qf=" + qf
    if(len(pf) > 0): solr_url += "&pf=" + pf
    if(ps != 1.0): solr_url += "&ps=" + str(ps)
    if(len(pf2) > 0): solr_url += "&pf2=" + pf2
    if(ps2 != 1.0): solr_url += "&ps2=" + str(ps2)
    if(len(pf3) > 0): solr_url += "&pf3=" + pf3
    if(ps3 != 1.0): solr_url += "&ps3=" + str(ps3)
    if(tibr != 0.0): solr_url += "&tie=" + str(tibr)
    solr_url += "&fl=*"
    solr_url += "&echoParams=all"
    solr_url += "&rows=25"
    solr_url += "&wt=json"
    solr_url += "&bf=pow(europeana_completeness,2)"
    qr = requests.get(solr_url)
    return qr.json()

def do_unweighted_query(q):
    solr_url = SOLR_SHARD_NOW8T + "?q=" + q + "&wt=json&rows=25&fl=*"
    qr = requests.get(solr_url)
    return qr.json()

def do_bm25f_query(q):
    solr_url = SOLR_SHARD_TEST + "?q=" + q + "&wt=json&rows=25&fl=*"
    qr = requests.get(solr_url)
    return qr.json()
"""
def instructions(request):
     return render(request, 'rankfiddle/instructions.html')
