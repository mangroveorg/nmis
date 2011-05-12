from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from main.views import main as main_index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nmis.views.home', name='home'),
    # url(r'^nmis/', include('nmis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^/?$', main_index),
    url(r'', include('nmis.main.urls')),
    url(r'^indicators/', include('nmis.indicator_management.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
)
