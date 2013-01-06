from django.conf.urls import patterns, include, url
from zivimap.api import WorkSpecResource

workspec_resource = WorkSpecResource()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^map/', include('zivimap.urls')),
    url(r'^api/', include(workspec_resource.urls)),
    # Examples:
    # url(r'^$', 'ziviweb.views.home', name='home'),
    # url(r'^ziviweb/', include('ziviweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
