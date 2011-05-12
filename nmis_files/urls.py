#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url

import nmis_files.views as views

urlpatterns = patterns('',
    url(r'^/?$', views.index, name='files-index'),
    url(r'^all/?$', views.all, name='files-all'),
    url(r'^info/(?P<pic_id>[a-zA-Z0-9\-\_\.]+)/?$', \
        views.info, name='file-info'),
    url(r'^fwd/(?P<pic_id>[a-zA-Z0-9\-\_\.]+)/(?P<format>[a-z0-9\_]+)?$', \
        views.forward, name='file-forward'),
    url(r'^magic/(?P<pic_id>[a-zA-Z0-9\-\_\.]+)/' \
         '(?P<command>[a-z0-9\-\=\_]+)?$', \
        views.magic_forward, name='file-magic'),
)
