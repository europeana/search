from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django import forms
from django.core import serializers
from .models import InitialItem, FieldName
import requests

SOLR_PROD = "http://sol1.eanadev.org:9191/solr/search_1/search"

class MLTParamsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        # item for which similarity will be computed
        inititem_choice = [('', '------------')]
        for row in InitialItem.objects.all().order_by('id')[0:250]:
            trunc_title = row.title[0:35]
            if(len(trunc_title) < len(row.title)): trunc_title = trunc_title + " ..."
            inititem_choice.append((row.id, trunc_title))
        num_items = len(inititem_choice) - 1 # account for null value
        self.fields['initial_item'] = forms.ChoiceField(label="Choose from top " + str(num_items) + " items (ordered by popularity)", choices=inititem_choice, widget=forms.Select(attrs={ 'id' : 'query-selector'}), initial='', required=False)

        # fields to use for similarity measurement
        fieldname_choice = [('', '------------')]
        for fieldname in FieldName.objects.all().order_by('field_name'):
            fieldname_choice.append((fieldname.field_name, fieldname.field_name))
        for i in range(1,11):
            self.fields['fieldname_' + str(i + 1)] = forms.ChoiceField(label="Similarity field " + str(i), choices=fieldname_choice, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'mlt-field'}))

        self.fields['mintf'] = forms.IntegerField(label="Min Term Frequency", min_value=1, max_value=100, initial=1, required=False, widget=forms.NumberInput({ 'id' : 'mintf' }))
        self.fields['mindf'] = forms.IntegerField(label="Min Doc Frequency", min_value=1, max_value=100, initial=1, required=False, widget=forms.NumberInput({ 'id' : 'mindf' }))
        self.fields['maxdf'] = forms.IntegerField(label="Max Doc Frequency", min_value=1, max_value=10000, initial=1, required=False, widget=forms.NumberInput({ 'id' : 'maxdf' }))
        self.fields['minwl'] = forms.IntegerField(label="Min Word Length", min_value=1, max_value=10, initial=5, required=False, widget=forms.NumberInput({ 'id' : 'minwl' }))
        self.fields['maxwl'] = forms.IntegerField(label="Max Word Length", min_value=0, max_value=25, initial=20,required=False, widget=forms.NumberInput({ 'id' : 'maxwl' }))
        self.fields['maxqt'] = forms.IntegerField(label="Max Query Terms", min_value=0, max_value=100, initial=10, required=False, widget=forms.NumberInput({ 'id' : 'maxqt' }))
        self.fields['maxntp'] = forms.IntegerField(label="Max Tokens", min_value=0, max_value=10000, initial=1000, required=False, widget=forms.NumberInput({ 'id' : 'maxqt' }))
        self.fields['boost'] = forms.BooleanField(label="Boost?", required=False, initial=True, widget=forms.CheckboxInput({ 'id' : 'boost' }))
        for i in range(1,11):
            self.fields['field_' + str(i)] = forms.ChoiceField(label="Field Name " + str(i), choices=fieldname_choice, initial='', required=False, widget=forms.Select(attrs={ 'class' : 'boost-field standard-boost-field'}))
            self.fields['field_boost_' + str(i)] = forms.DecimalField(label="Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False, widget=forms.NumberInput(attrs={ 'class' : 'standard-boost-factor boost-factor'}))



def index(request):

    if request.method == 'POST':
        quf = MLTParamsForm(request.POST)
        if(quf.is_valid()):
            """wv = quf.cleaned_data['weight_views']
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
            results = do_query(wv, q, boosts, phrase_boosts, ps, bigram_boosts, ps2, trigram_boosts, ps3, tibr)
            return render(request, 'rankfiddle/rankfiddle.html', {'form':quf, 'params': build_params(results)})"""
            return("<h1>Form submitted</h1>;l]"
                   " ")
    else:
        quf = MLTParamsForm()
    return render(request, 'mltfiddle/mltfiddle.html', {'form':quf })

def retrieve_init_item(search_obj):
    item_id = search_obj.GET['item_id']
    iidb = InitialItem.objects.get(id=item_id)
    iidb_j = dict()
    iidb_j['title'] = iidb.title
    iidb_j['description'] = iidb.description
    iidb_j['europeana_id'] = iidb.europeana_id
    iidb_j['url'] = iidb.url
    iidb_j['thumbnail'] = iidb.thumbnail
    iidb_j['resource_type'] = iidb.resource_type
    iidb_j['original_page'] = iidb.original_page
    iidb_j['data_provider'] = iidb.data_provider
    return JsonResponse(iidb_j)

def update_with_url(request):

    alladds = ""
    for row in InitialItem.objects.all():
        quoted_uri = row.original_page
        new_uri = quoted_uri[1:]
        row.original_page = new_uri
        row.save()
    return HttpResponse("<h1>done</h1>")


# note that the MLTHandler is already defined in the solrconfig.xml file
# and prepopulated with default values. We will need to explicitly override
# if no value is supplied by the user
# we'll also need to supply mlt.match.include=false, mlt.match.offset=0, and mlt.interestingTerms=details

