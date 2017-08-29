from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='collectionbuilder'),
    url(r'init$', views.init, name='newquery'),
    url(r'new-clause$', views.newclause, name='newclause'),
    url(r'new-clause-group$', views.newclausegroup, name='newclause'),
    url(r'delete-cl-element$', views.deleteclelement, name='deletion'),
    url(r'facet-values$', views.facetvalues, name='facetvalues'),
    url(r'translate$', views.translate, name='translate'),
    url(r'instructions$', views.instructions, name='instructions'),

]
