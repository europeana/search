from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='rankfiddle_tool'),
    url(r'instructions$', views.instructions, name='instructions'),

]