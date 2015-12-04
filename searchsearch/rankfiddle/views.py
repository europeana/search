from django.shortcuts import render
from django import forms
from .models import Query, CandidateBoostFields
from django.http import HttpResponse, JsonResponse
from .models import MAX_QUERY_LENGTH
import requests
import json

SOLR_SHARD_SIMPLE = 'http://sol1.ingest.eanadev.org:9191/solr/search_1/search'

class QueryBoostForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        fields = [('', '----------')]
        # we can set an arbitrary number of field + boost values
        # here we set 50 as the upper limit (though 15 is probably too many)
        # we'll use JS to hide all but the first handful on the frontend
        # and supply an 'add' button to reveal these progressively as complexity increases
        for row in CandidateBoostFields.objects.all().order_by('field_name'):
            fields.append((row.field_name, row.field_name))
        for i in range(1,51):
            self.fields['field_' + str(i)] = forms.ChoiceField(label="Field Name " + str(i), choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field'}))
            self.fields['field_boost_' + str(i)] = forms.DecimalField(label="Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'boost-factor'}))

    query_choice = [('', '------------')]
    for row in Query.objects.all().order_by('query_text'):
        query_choice.append((row.query_text, row.query_text))
    query = forms.ChoiceField(label="Query", choices=query_choice, widget=forms.Select(attrs={ 'id' : 'query-selector'}), initial='')
    pf = forms.DecimalField(label="Phrase Field", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'phrase'}))
    ps = forms.DecimalField(label="Phrase Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    pf2 = forms.DecimalField(label="Phrase Bigram", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'phrase'}))
    ps2 = forms.DecimalField(label="Bigram Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    pf3 = forms.DecimalField(label="Phrase Trigram", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'phrase'}))
    ps3 = forms.DecimalField(label="Trigram Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    tibr = forms.DecimalField(label="Tiebreak (0.0 - 1.0)", max_digits=2, decimal_places=1, max_value=1.0, min_value=0.0, initial=0.0)

def index(request):

    if request.method == 'POST':
        quf = QueryBoostForm(request.POST)
        if(quf.is_valid()):
            q = quf.cleaned_data['query'] if quf.cleaned_data['query'].strip() != '' else '*:*'
            boosts = ""
            for i in range(1,51):
                field_name = 'field_' + str(i)
                if(quf.cleaned_data[field_name] != ''):
                    boost = quf.cleaned_data[field_name] + "^" + str(quf.cleaned_data['field_boost_' + str(i)])
                    boosts = boosts + boost + " "
            pf = quf.cleaned_data['pf']
            ps = quf.cleaned_data['ps']
            pf2 = quf.cleaned_data['pf2']
            ps2 = quf.cleaned_data['ps2']
            pf3 = quf.cleaned_data['pf3']
            ps3 = quf.cleaned_data['ps3']
            tibr = quf.cleaned_data['tibr']
            results = do_query(q, boosts, pf, ps, pf2, ps2, pf3, ps3, tibr)
            return render(request, 'rankfiddle/rankfiddle.html', {'form':quf, 'params':results['responseHeader']['params'], 'docs':results['response']['docs'], 'result_count':results['response']['numFound']})
    else:
        quf = QueryBoostForm()
    return render(request, 'rankfiddle/rankfiddle.html', {'form':quf })

def do_query(q, qf, pf, ps, pf2, ps2, pf3, ps3, tibr):
    # TODO: need to control for defaults already present in bm25f handler (init to 0)
    solr_url = SOLR_SHARD_SIMPLE + "?q={!type=edismax}" + q;
    # solr_url = SOLR_SHARD_SIMPLE + "?q=" + q;
    if(len(qf) > 0):solr_url += "&qf=" + qf
    if(pf != 1.0): solr_url += "&pf=" + str(pf)
    if(ps != 1.0): solr_url += "&ps=" + str(ps)
    if(pf2 != 1.0): solr_url += "&pf2=" + str(pf2)
    if(ps2 != 1.0): solr_url += "&ps2=" + str(ps2)
    if(pf3 != 1.0): solr_url += "&pf3=" + str(pf3)
    if(ps3 != 1.0): solr_url += "&ps3=" + str(ps3)
    if(tibr != 0.0): solr_url += "&tie=" + str(tibr)
    solr_url += "&echoParams=all"
    solr_url += "&rows=25"
    solr_url += "&wt=json"
    solr_url += "&bf=pow(europeana_completeness,2)"
    solr_url += "&bq=description:*^1000"
    qr = requests.get(solr_url)
    return qr.json()

    # current settings
    # title^10
    # subject^15
    # description^10
    # proxy_dc_creator^15
    # text^1
    # tie=0.8
    # bf as above