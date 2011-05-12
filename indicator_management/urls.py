from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'', views.list_indicators),
#    url(r'^indicators/(?P<region_path>\S*)', views.region_navigation),
)
