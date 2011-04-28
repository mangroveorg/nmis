from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^profiles/(?P<region_path>\S*)', views.region_navigation),
    url(r'^spreadsheets/$', views.spreadsheets),
    url(r'^spreadsheets/(?P<sheet_name>\S+)$', views.spreadsheet_json),
)
