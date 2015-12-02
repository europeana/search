from django.shortcuts import render
from django import forms
from .models import Query, CandidateBoostFields
from django.http import HttpResponse
from .models import MAX_QUERY_LENGTH
import pysolr

SOLR_SHARD_SIMPLE = 'http://sol1.ingest.eanadev.org:9191/solr/search_test_shard1_replica1/simple'

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
            self.fields['field_' + str(i)] = forms.ChoiceField(label="Field Name " + str(i), choices=fields, initial='', required=False)
            self.fields['field_boost_' + str(i)] = forms.DecimalField(label="Field Boost " + str(i), max_digits=4, decimal_places=1, initial=1.0, required=False)

    query_choice = [('', '------------')]
    for row in Query.objects.all().order_by('query_text'):
        query_choice.append((row.query_text, row.query_text))
    query = forms.ChoiceField(label="Query", choices=query_choice, widget=forms.Select(attrs={ 'id' : 'query-selector'}), initial='')
    pf = forms.DecimalField(label="Phrase Field", max_digits=4, decimal_places=1, initial=1.0)
    ps = forms.DecimalField(label="Phrase Slop", max_digits=4, decimal_places=1, initial=1.0)
    pf2 = forms.DecimalField(label="Phrase Bigram", max_digits=4, decimal_places=1, initial=1.0)
    ps2 = forms.DecimalField(label="Bigram Slop", max_digits=4, decimal_places=1, initial=1.0)
    pf3 = forms.DecimalField(label="Phrase Trigram", max_digits=4, decimal_places=1, initial=1.0)
    ps3 = forms.DecimalField(label="Trigram Slop", max_digits=4, decimal_places=1, initial=1.0)
    tibr = forms.DecimalField(label="Tiebreak (0.0 - 1.0)", max_digits=2, decimal_places=1, max_value=1.0, min_value=0.0, initial=0.0)




def index(request):

    if request.method == 'POST':
        quf = QueryBoostForm(request.POST)
        if(quf.is_valid()):
            q = quf.cleaned_data['query']
            boosts = ""
            for i in range(1,51):
                field_name = 'field_' + str(i)
                if(quf.cleaned_data[field_name] != ''):
                    boost = quf.cleaned_data[field_name] + "^" + str(quf.cleaned_data['field_boost_' + str(i)])
                    boosts = boosts + boost + " "
            return HttpResponse(do_query(q, boosts))
    else:
        quf = QueryBoostForm()
    return render(request, 'rankfiddle/rankfiddle.html', {'form':quf })

def do_query(q, qf):
    # TODO: existing Solr clients not customisable enough, so we need to build the query and parse the results manually
    solr_url = SOLR_SHARD_SIMPLE + "?q=" + q;
    if(len(qf) > 0): solr_url = solr_url + "&qf=" + qf
    solr_url = solr_url + "wt=python"
    return solr_url