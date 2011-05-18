from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from main.views import main as main_index
from tiles.views import tile_cache

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('nmis.main.urls')),
    url(r'^indicators/', include('nmis.indicator_management.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^tiles/(?P<tile_path>.*)$', tile_cache),
    url(r'^pictures/', include('nmis.nmis_files.urls')),
)
