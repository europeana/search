from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib import admin
urlpatterns = [

    url(r'^volgus/', include('mobsource.urls', namespace='mobsource'), name="volgus"),
    url(r'^$', RedirectView.as_view(permanent=True, url="/volgus")),
    url(r'^accounts/register/complete/$', RedirectView.as_view(permanent=True, url="/volgus/referendum")),
    url(r'^accounts/profile/$', RedirectView.as_view(permanent=True, url="/volgus/referendum")),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^admin/', include(admin.site.urls)),

]