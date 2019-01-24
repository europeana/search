from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='collectionbuilder'),
    url(r'init$', views.init, name='newquery'),
    url(r'new-clause$', views.newclause, name='newclause'),
    url(r'new-clause-group$', views.newclausegroup, name='newclausegroup'),
    url(r'delete-cl-element$', views.deleteclelement, name='deletion'),
    url(r'facet-values$', views.facetvalues, name='facetvalues'),
    url(r'translate$', views.translate, name='translate'),
    url(r'updatevalues$', views.updatevalues, name='updatevalues'),
    url(r'update-operator$', views.updateoperator, name='updateoperator'),
    url(r'update-negated-status$', views.updatenegated, name="updatenegated"),
    url(r'new-expansion-group$', views.newexpansiongroup, name="newexpansiongroup"),    
    url(r'getfullquery$', views.getfullquery, name='getfullquery'),
    url(r'getfullquery$', views.getfullquery, name='getfullquery'),
    url(r'deprecate$', views.changedeprecate, name='changedeprecate'),
    url(r'instructions$', views.instructions, name='instructions'),
    url(r'convert-to-cg$', views.converttoclausegroup, name="converttoclausegroup"),
    url(r'convert-to-cl$', views.converttoclause, name="converttoclause"),
    url(r'force-all-operators$', views.forcealloperators, name="forcealloperators"),
    url(r'get-saved-queries$', views.getsavedqueries, name="getsavedqueries"),
    url(r'get-hit-count$', views.gethitcount, name="gethitcount"),
    url(r'open-query', views.openquery, name="openquery"),
    url(r'save-query', views.savequery, name="savequery"),
    
]
