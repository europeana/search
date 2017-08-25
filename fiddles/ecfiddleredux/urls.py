from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='ecfiddleredux_tool'),
    url(r'instructions$', views.reduxinstructions, name='reduxinstructions'),

]
