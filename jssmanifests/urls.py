
from django.conf.urls import patterns, include, url

from jssmanifests import xmlviews
from jssmanifests import testviews

urlpatterns = [
    url(r'^testindex$', testviews.index),
    url(r'^xml/(?P<manifest_name>[^/]+)/?$', xmlviews.manifest,
                                                  name='xml-manifest'),
]


