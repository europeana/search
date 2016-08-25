from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='mltfiddle_tool'),
    url(r'^inititem', views.retrieve_init_item),
    url(r'^relateditems$', views.retrieve_related_items),

]