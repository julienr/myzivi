from django.conf.urls import patterns, include, url
from zivimap.api import *
from tastypie.api import Api
import ziviweb.settings as settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name=settings.API_VERSION)
v1_api.register(AddressResource())
v1_api.register(WorkSpecResource())
v1_api.register(MapSearchResource())

print v1_api.urls

urlpatterns = patterns('',
    url(r'^$', 'zivimap.views.index'),
    url(r'^map/', include('zivimap.urls')),
    url(r'^api/', include(v1_api.urls)),
    # Examples:
    # url(r'^$', 'ziviweb.views.home', name='home'),
    # url(r'^ziviweb/', include('ziviweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
