from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django import forms
from django.core import serializers
from .models import InitialItem, FieldName
import requests
import json


SOLR_MLT = "http://sol7.eanadev.org:9191/solr/search_2/mlt?wt=json"
SOLR_SEARCH = "http://sol7.eanadev.org:9191/solr/search_2/mlt"

class InitialItemForm(forms.Form):

    def __init__(self, *args, **kwargs):
        # initial search term
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields['searchterm'] = forms.CharField(label='Original search term', max_length=200, required=True)

class MLTParamsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # fields to use for similarity measurement
        fieldname_choice = [('', '------------')]
        for fieldname in FieldName.objects.all().order_by('field_name'):
            fieldname_choice.append((fieldname.field_name, fieldname.field_name))
        self.fields['field_1'] = forms.ChoiceField(label=" Similarity Field Name 1", choices=fieldname_choice, required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}),initial="title")
        self.fields['field_boost_1'] = forms.DecimalField(label="Boost", max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))
        self.fields['field_2'] = forms.ChoiceField(label=" Similarity Field Name 2", choices=fieldname_choice, required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}),initial="description")
        self.fields['field_boost_2'] = forms.DecimalField(label="Boost", max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))
        self.fields['field_3'] = forms.ChoiceField(label=" Similarity Field Name 3", choices=fieldname_choice, required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}),initial="subject")
        self.fields['field_boost_3'] = forms.DecimalField(label="Boost", max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))
        self.fields['field_4'] = forms.ChoiceField(label=" Similarity Field Name 4", choices=fieldname_choice, required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}),initial="creator")
        self.fields['field_boost_4'] = forms.DecimalField(label="Boost", max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))
        for i in range(5,11):
            self.fields['field_' + str(i)] = forms.ChoiceField(label=" Similarity Field Name " + str(i), choices=fieldname_choice, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}))
            self.fields['field_boost_' + str(i)] = forms.DecimalField(label="Boost" + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))

        self.fields['mintf'] = forms.IntegerField(label="Min Term Frequency", min_value=1, max_value=100, initial=1, required=False, widget=forms.NumberInput({ 'id' : 'mintf' }))
        self.fields['mindf'] = forms.IntegerField(label="Min Doc Frequency", min_value=1, max_value=100, initial=1, required=False, widget=forms.NumberInput({ 'id' : 'mindf' }))
        self.fields['maxdf'] = forms.IntegerField(label="Max Doc Frequency", min_value=-1, max_value=10000000, initial=-1, required=False, widget=forms.NumberInput({ 'id' : 'maxdf' }))
        self.fields['minwl'] = forms.IntegerField(label="Min Word Length", min_value=1, max_value=10, initial=3, required=False, widget=forms.NumberInput({ 'id' : 'minwl' }))
        self.fields['maxwl'] = forms.IntegerField(label="Max Word Length", min_value=0, max_value=500, initial=150,required=False, widget=forms.NumberInput({ 'id' : 'maxwl' }))
        self.fields['maxqt'] = forms.IntegerField(label="Max Query Terms", min_value=0, max_value=100, initial=10, required=False, widget=forms.NumberInput({ 'id' : 'maxqt' }))
        self.fields['maxntp'] = forms.IntegerField(label="Max Tokens", min_value=0, max_value=10000, initial=1000, required=False, widget=forms.NumberInput({ 'id' : 'maxntp' }))
        self.fields['boost'] = forms.BooleanField(label="Boost?", required=False, initial=True, widget=forms.CheckboxInput({ 'id' : 'boost' }))

def index(request):
    ini = InitialItemForm()
    quf = MLTParamsForm()
    return render(request, 'mltfiddle/mltfiddle.html', {'searchform':ini, 'mltform':quf })

def retrieve_init_item(search_obj):
    terms = search_obj.GET['searchterms']
    if(":" in terms):
        (field, term) = terms.split(":")
        field = field + ":"
    else:
        field = ""
        term = terms
    term = term.replace("\"", "")
    qry = SOLR_SEARCH + "?wt=json&rows=1&fl=*&q=" + field + "\"" + term + "\""
    res = requests.get(qry)
    res_j = res.json()
    iidb_j = dict()
    item = dict()
    try:
        item = res_j['match']['docs'][0]
    except:
        iidb_j['europeana_id'] = 'no-item-found'
        return JsonResponse(iidb_j)
    try:
        iidb_j['title'] = item['title'][0]
    except:
        pass
    try:
        iidb_j['description'] = item['description'][0]
    except:
        pass
    iidb_j['europeana_id'] = item['europeana_id']
    try:
        iidb_j['url'] = item['europeana_aggregation_edm_landingPage']
    except:
        pass
    try:
        iidb_j['thumbnail'] = item['provider_aggregation_edm_object'][0]
    except:
        pass
    try:
        iidb_j['resource_type'] = item['proxy_edm_type'][0]
    except:
        pass
    try:
        iidb_j['original_page'] = item['provider_aggregation_edm_isShownAt'][0]
    except:
        pass
    try:
        iidb_j['data_provider'] = item['DATA_PROVIDER'][0]
    except:
        pass
    return JsonResponse(iidb_j)

def retrieve_related_items(search_obj):
    root_query = "q=europeana_id:\"" + search_obj.GET['europeana_id'] + "\""
    fields = "fl=*"
    mintf = "mlt.mintf=" + str(search_obj.GET['mintf'])
    mindf = "mlt.mindf=" + str(search_obj.GET['mindf'])
    maxdf = "mlt.maxdf=" + str(search_obj.GET['maxdf'])
    minwl = "mlt.minwl=" + str(search_obj.GET['minwl'])
    maxwl = "mlt.maxwl=" + str(search_obj.GET['maxwl'])
    maxqt = "mlt.maxqt=" + str(search_obj.GET['maxqt'])
    maxntp = "mlt.maxntp=" + str(search_obj.GET['maxntp'])
    boost_bool = "true" if search_obj.GET['boost'] == "on" else "false"
    boost = "mlt.boost=" + boost_bool
    searchfields = []
    boostfields = []
    for f in search_obj.GET.keys():
        if('boostfield' in f):
            num = f.split("_")[1]
            bf = "boostfactor_" + str(num)
            boostfield = search_obj.GET[f]
            boostfactor = search_obj.GET[bf]
            field_w_boost = boostfield + "^" + str(boostfactor)
            boostfields.append(field_w_boost)
            searchfields.append(boostfield)
    boostparams = "qf=" + " ".join(boostfields) if len(boostfields) > 0 else ""
    fields = "mlt.fl=" + ",".join(searchfields)
    params = [root_query, fields, mintf, mindf, minwl, maxwl, maxqt, maxntp, boost, fields]
    if(str(search_obj.GET['maxdf']) != "-1"): params.append(maxdf)
    if len(boostparams) > 0: params.append(boostparams)
    qs = "&".join(params)
    qry = SOLR_MLT + "&" + qs
    res = requests.get(qry)
    res_j = res.json()
    res_j['query'] = qry
    return JsonResponse(res_j)

# note that the MLTHandler is already defined in the solrconfig.xml file
# and prepopulated with default values. We will need to explicitly override
# if no value is supplied by the user
# we'll also need to supply mlt.match.include=false, mlt.match.offset=0, and mlt.interestingTerms=details

