from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^Agents$', views.agent_list, name='agent_list'),
    url(r'^Agent/(?P<agent_id>Q[0-9]+)', views.agent, name='agent'),
    url(r'^Network/(?P<agent_id>Q[0-9]+)', views.network, name='network')

]