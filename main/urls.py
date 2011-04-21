from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^by-lga/', views.by_lga)
)

