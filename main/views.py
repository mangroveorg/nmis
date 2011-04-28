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

def data_for_entity(entity):
    pass

def mdg_table_from_data(data):
    '''This function maps a list of (DataDictType, value) to the MDG table json format.

    {
  "variables": {
    "1": {
      "name": "Number of Mice caught by Falcons",
      "data_type": "integer",
      "display_order": 2650,
      "values": {
        "2010": 5,
        "2009": 15
      },
      "subgoal": "1.1",
      "subgroup": "Male Mice",
      "goal": "1"
    },
    "3": {
      "name": "Number of Mice caught by Falcons",
      "data_type": "integer",
      "display_order": 2650,
      "values": {
        "2010": 9,
        "2009": 35
      },
      "subgoal": "1.1",
      "subgroup": "Total",
      "goal": "1"
    },
    "2": {
      "name": "Number of Mice caught by Falcons",
      "data_type": "integer",
      "display_order": 2650,
      "values": {
        "2010": 4,
        "2009": 20
      },
      "subgoal": "1.1",
      "subgroup": "Female Mice",
      "goal": "1"
    },
    "5": {
      "name": "Average weight of Falcon",
      "data_type": "decimal",
      "display_order": 2430,
      "values": {
        "2010": 12.33,
        "2009": 20.94
      },
      "subgoal": null,
      "subgroup": null,
      "goal": "6"
    },
    "4": {
      "name": "Professional Falconers",
      "data_type": "integer",
      "display_order": 2540,
      "values": {
        "2010": 10,
        "2009": 4
      },
      "subgoal": "2.3",
      "subgroup": "Male",
      "goal": "2"
    }
  },
  "years": [
    2010,
    2009
  ]
}
    '''
    variables = {}
    years = []
    for d in data:
