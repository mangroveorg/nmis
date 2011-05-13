from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^/?$', views.region_navigation, {'region_path': 'nigeria'}),
    url(r'^profiles/(?P<region_path>\S*)', views.region_navigation),
    url(r'^LGAs/', views.lgas_json, name='lgas-list'),
)
