from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from django.template.defaultfilters import slugify
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import get_entities_by_type, get_entities_in
from main.region_thing import RegionThing
import json

def main(request):
    return render_to_response('index.html')

def region_navigation(request, region_path):
    context = RequestContext(request)
    # profile_root is the url root for the profiles
    # probably could use django's lookup thing for this
    context.profile_root = "/profiles/"
    country_root_object = region_root_object()
    if region_path == "": return HttpResponseRedirect("/profiles/nigeria")
    
    #query country for sub sections
    region_thing_object = country_root_object.find_child_by_slug_array(region_path.split("/"))
    
    # see nmis/static/mdg_sample.json for the example of how the MDG data should be
    # structured
    context.mdg_data_url = "/static/mdg_sample.json"
    # if we want to specify parameters to be appended to the URL, 
    # we can pass them here
    mdg_data_query_params = {}
    context.mdg_data_query_params = json.dumps(mdg_data_query_params)
    
    sample_dict = region_thing_object.to_dict()
    context.region_hierarchy = region_thing_object.context_dict(2)
    return render_to_response("region_navigation.html", context_instance=context)

def region_root_object():
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE']
    )
    country = get_entities_by_type(dbm, 'Country')[0]
    country_name = country.aggregation_paths['_geo'][-1]
    country_slug = slugify(country_name)
    country_region_thing = RegionThing(
        name=country_name,
        slug=country_slug,
        entity_id=country.id,
        server=dbm.server,
        database=dbm.database_name
    )
    states = get_entities_in(dbm, country.aggregation_paths['_geo'], 'State')
    for state in states:
        state_name = state.aggregation_paths['_geo'][-1]
        state_slug = slugify(state_name)
        state_region_thing = RegionThing(
            name=state_name,
            slug=state_slug,
            entity_id=state.id,
            server=dbm.server,
            database=dbm.database_name
        )
        lgas = get_entities_in(dbm, state.aggregation_paths['_geo'], 'LGA')
        for lga in lgas:
            lga_name = lga.aggregation_paths['_geo'][-1]
            lga_slug = slugify(lga_name)
            lga_region_thing = RegionThing(
                name=lga_name,
                slug=lga_slug,
                entity_id=lga.id,
                server=dbm.server,
                database=dbm.database_name
            )
            state_region_thing._set_subregions([lga_region_thing])
        country_region_thing._set_subregions([state_region_thing])

    return country_region_thing