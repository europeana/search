import json
from django import forms
from django.shortcuts import render, HttpResponse
from django.db.models import Q, Count
from .models import Agent, Work, EuropeanaWork, SocialRelation, RelationshipType, AgentImage, AgentRole

class RoleFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

    all_roles = AgentRole.objects.all().distinct('pref_label').order_by('pref_label')
    role_options = []
    for role in all_roles:
        role_options.append((role.pref_label, role.pref_label.capitalize()))
    role_select = forms.MultipleChoiceField(choices=role_options, label="Filter by roles", required=False, widget=forms.CheckboxSelectMultiple)


class RoleOrderForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

    orders = [

        ('-social_relation', 'Relationship number (highest -> lowest)'),
        ('social_relation', 'Relationship number (lowest -> highest)'),
        ('birthdate', 'Birthdate (earliest -> latest)'),
        ('-birthdate', 'Birthdate (latest -> earliest)'),
        ('pref_label', 'Name (A -> Z)'),
        ('-pref_label', 'Name (Z -> A)')
    ]
    order_select = forms.ChoiceField(choices=orders, label="Order by", required=True, widget=forms.RadioSelect)

def agent_list(request):
    if request.method == "POST":
        role_form = RoleFilterForm(request.POST)
        order_form = RoleOrderForm(request.POST)
        if(role_form.is_valid() & order_form.is_valid()):
            roles = role_form.cleaned_data['role_select']
            order = order_form.cleaned_data['order_select']
            order_field = order.replace("-", "")
            sign = "-" if len(order_field) < len(order) else ""
            qs = [Q(agentrole__pref_label=role) for role in roles]
            query = qs.pop()
            for q in qs:
                query |= q
            if(order_field == 'social_relation'):
                all_agents = Agent.objects.filter(query).select_related('portrait').annotate(criterion = Count(order_field)).order_by(sign + "criterion").distinct()
            else:
                all_agents = Agent.objects.filter(query).select_related('portrait').order_by(order).distinct()
            role_form = RoleFilterForm(initial={ 'role_select' : roles })
            order_form = RoleOrderForm(initial={ 'order_select' : order })
            context = { 'agents' : all_agents, 'role_form' : role_form, 'order_form' : order_form }
            return render(request, 'remfriends/agents.html', context)
    else:
        # all_agents = Agent.objects.filter(agentrole__pref_label='painter').select_related('portrait').order_by('birthdate').distinct()
        all_agents = Agent.objects.filter(agentrole__pref_label='painter').select_related('portrait').annotate(num_friends = Count('social_relation')).order_by('-num_friends').distinct()
        role_form = RoleFilterForm(initial={ 'role_select' : ['painter'] })
        order_form = RoleOrderForm(initial={ 'order_select' : '-social_relation'})
        context = { 'agents' : all_agents, 'role_form' : role_form, 'order_form' : order_form }
        return render(request, 'remfriends/agents.html', context)

def agent(request, agent_id):
    agent_id = "http://www.wikidata.org/entity/" + agent_id
    agent = Agent.objects.get(wdid=agent_id)
    works = Work.objects.filter(creator__wdid=agent_id).order_by("pref_label").distinct()
    eworks = EuropeanaWork.objects.filter(creator__wdid=agent_id).order_by("pref_label").distinct()
    outward_relations = SocialRelation.objects.filter(active=agent_id).select_related("relationship_type")
    roles = AgentRole.objects.filter(agent=agent_id)
    depicted_in_euro = EuropeanaWork.objects.filter(subject=agent_id)
    context = { 'agent' : agent, 'works' : works, 'europeana_works' : eworks, 'outward_relations' : outward_relations, 'as_subject_eur' : depicted_in_euro, 'roles' : roles }
    return render(request, 'remfriends/agent.html', context)

def network(request, agent_id):
    agent_id = "http://www.wikidata.org/entity/" + agent_id
    outward_relations = SocialRelation.objects.filter(active=agent_id).select_related("relationship_type")
    orels = []
    for row in outward_relations:
        portrait = "None"
        try:
            portrait = row.passive.portrait.image_url
        except Exception:
            pass
        info = [row.active.wdid, row.active.pref_label, row.relationship_type.pref_label, row.passive.pref_label, row.passive.wdid, portrait]
        orels.append(info)
    return HttpResponse(json.dumps(orels))

def intro(request):
    return render(request, 'remfriends/intro.html')