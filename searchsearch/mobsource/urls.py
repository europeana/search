from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^referendum$', views.searchform, name='searchform'),
    url(r'^loc', views.do_query, name='query_execute'),

]