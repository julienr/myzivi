import ziviweb.settings as settings
from django.conf.urls import patterns, include, url
from zivimap import views
from zivimap.api import WorkSpecResource
from tastypie.api import Api

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),

)
