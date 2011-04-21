from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from main.views import main as main_index
from settings import MEDIA_ROOT

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nmis.views.home', name='home'),
    # url(r'^nmis/', include('nmis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', main_index),
    url(r'', include('nmis.main.urls')),
    (r'^static/(?P<path>.+)$', 'django.views.static.serve', {'document_root' : MEDIA_ROOT}),
)
