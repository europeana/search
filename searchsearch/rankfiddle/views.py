from django.shortcuts import render
from django import forms
from .models import Query, CandidateBoostFields
from django.http import HttpResponse, JsonResponse
from .models import MAX_QUERY_LENGTH
import requests
import json

SOLR_SHARD_SIMPLE = 'http://sol1.eanadev.org:9191/solr/search_1/search'

class QueryBoostForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        fields = [('', '----------')]
        # we can set an arbitrary number of field + boost values
        # for both boost and phrase fields
        # here we set 15 as the upper limit
        # we'll use JS to hide all but the first handful on the frontend
        # and supply an 'add' button to reveal these progressively as complexity increases
        for row in CandidateBoostFields.objects.all().order_by('field_name'):
            fields.append((row.field_name, row.field_name))

        # standard field boosts
        for i in range(1,16):
            self.fields['field_' + str(i)] = forms.ChoiceField(label="Field Name " + str(i), choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}))
            self.fields['field_boost_' + str(i)] = forms.DecimalField(label="Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))
        # phrase boosts
        for i in range(1,11):
            self.fields['phrase_field_' + str(i)] = forms.ChoiceField(label="Phrase Field Name " + str(i), choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field phrase-boost-field'}))
            self.fields['phrase_field_boost_' + str(i)] = forms.DecimalField(label="Phrase Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'boost-factor phrase-boost-factor'}))
        # bigram boosts
        for i in range(1,11):
            self.fields['bigram_field_' + str(i)] = forms.ChoiceField(label="Bigram Field Name " + str(i), choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field bigram-boost-field'}))
            self.fields['bigram_field_boost_' + str(i)] = forms.DecimalField(label="Bigram Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'boost-factor bigram-boost-factor'}))
        # trigram boosts
        for i in range(1,11):
            self.fields['trigram_field_' + str(i)] = forms.ChoiceField(label="Trigram Field Name " + str(i), choices=fields, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field trigram-boost-field'}))
            self.fields['trigram_field_boost_' + str(i)] = forms.DecimalField(label="Trigram Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'boost-factor trigram-boost-factor'}))

    query_choice = [('', '------------')]
    for row in Query.objects.all().order_by('query_text'):
        query_choice.append((row.query_text, row.query_text))
    query_freetext = forms.CharField(label="Query", max_length=200, widget=forms.TextInput(attrs={ 'id' : 'query-freetext'}), initial='', required=False)
    query_dropdown = forms.ChoiceField(label="or choose from top queries", choices=query_choice, widget=forms.Select(attrs={ 'id' : 'query-selector'}), initial='', required=False)
    ps = forms.DecimalField(label="Phrase Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    ps2 = forms.DecimalField(label="Bigram Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    ps3 = forms.DecimalField(label="Trigram Slop", max_digits=4, decimal_places=1, initial=1.0, widget=forms.NumberInput(attrs={ 'class' : 'slop'}))
    tibr = forms.DecimalField(label="Tiebreak (0.0 - 1.0)", max_digits=2, decimal_places=1, max_value=1.0, min_value=0.0, initial=0.0)

def index(request):

    if request.method == 'POST':
        quf = QueryBoostForm(request.POST)
        if(quf.is_valid()):
            query_freetext = quf.cleaned_data['query_freetext'].strip()
            query_dropdown = quf.cleaned_data['query_dropdown'].strip()
            q = query_freetext if query_freetext != '' else query_dropdown
            q = q if q != '' else '*:*'
            boosts = build_boosts(quf.cleaned_data, "field", 16)
            phrase_boosts = build_boosts(quf.cleaned_data, "phrase_field", 11)
            bigram_boosts = build_boosts(quf.cleaned_data, "trigram_field", 11)
            trigram_boosts = build_boosts(quf.cleaned_data, "bigram_field", 11)
            ps = quf.cleaned_data['ps']
            ps2 = quf.cleaned_data['ps2']
            ps3 = quf.cleaned_data['ps3']
            tibr = quf.cleaned_data['tibr']
            results = do_query(q, boosts, phrase_boosts, ps, bigram_boosts, ps2, trigram_boosts, ps3, tibr)
            return render(request, 'rankfiddle/rankfiddle.html', {'form':quf, 'params':results['responseHeader']['params'], 'docs':results['response']['docs'], 'result_count':results['response']['numFound']})
    else:
        quf = QueryBoostForm()
    return render(request, 'rankfiddle/rankfiddle.html', {'form':quf })

def build_boosts(cleaned_data, field_name, max_fields=20):
    boosts = ""
    for i in range(1,max_fields):
        now_fn = field_name + "_" + str(i)
        if(cleaned_data[now_fn] != ''):
            field_boost = field_name + "_boost_" + str(i)
            boost = cleaned_data[now_fn] + "^" + str(cleaned_data[field_boost])
            boosts += boost + " "
    return boosts

def do_query(q, qf, pf, ps, pf2, ps2, pf3, ps3, tibr):
    # TODO: need to control for defaults already present in bm25f handler (init to 0)
    solr_url = SOLR_SHARD_SIMPLE + "?q={!type=edismax}" + q;
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
    print(solr_url)
    qr = requests.get(solr_url)
    print(qr)
    return qr.json()

def instructions(request):
     return render(request, 'rankfiddle/instructions.html')

