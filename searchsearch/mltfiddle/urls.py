from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='mltfiddle_tool'),
    url(r'^inititem', views.retrieve_init_item),
#    url(r'instructions$', views.instructions, name='instructions'),

]