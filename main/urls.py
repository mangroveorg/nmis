from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^profiles/(?P<region_path>\S*)', views.region_navigation),
    url(r'^LGAs.json?', views.lgas_json, name='lgas-list'),
)
