from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext, loader as template_loader
from django.template.defaultfilters import slugify
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import get_entities_by_type, get_entities_in
from main.region_thing import RegionThing, import_region_thing_from_dict
from helpers import read_required
import json

@read_required()
def main(request):
    return render_to_response('index.html')
    
import widgets
import widget_data

def region_navigation(request, region_path):
    context = RequestContext(request)
    # profile_root is the url root for the profiles
    # probably could use django's lookup thing for this
    context.profile_root = "/profiles/"
    country_root_object = region_root_object()
    if region_path == "": return HttpResponseRedirect("/profiles/nigeria")
    
    #query country for sub sections
    region_thing_object = country_root_object.find_child_by_slug_array(region_path.split("/"))
    
    widget_ids, include_templates = widgets.widget_includes_by_region_level(len(region_thing_object.ancestors()))
    context.widgets = include_templates
    context.entity = region_thing_object.entity
    
    #what goes on behind the scenes that you don't need to edit--
    for widget_id in widget_ids:
        try:
            context.__dict__[widget_id] = getattr(widget_data, widget_id)(region_thing=region_thing_object)
        except:
            context.__dict__[widget_id] = False
    
    sample_dict = region_thing_object.to_dict()
    context.region_hierarchy = region_thing_object.context_dict(2)
    return render_to_response("region_navigation.html", context_instance=context)

import spreadsheet_display

def spreadsheet_json(request, sheet_name):
    "This is pulled by JSON and handled in the page."
    output = spreadsheet_display.for_display(sheet_name)
    # if display_method=="django_template":
    #     context = RequestContext(request)
    #     context.spreadsheet_name = output.get(u'name')
    #     output[u'html'] = \
    #         template_loader.render_to_string("spreadsheet_partial.html", context_instance=context)
    return HttpResponse(json.dumps(output))

def spreadsheets(request):
    context = RequestContext(request)
    context.spreadsheet_types = spreadsheet_display.LISTS
    return render_to_response("spreadsheets.html", context_instance=context)

NIGERIA_REGION_CACHE = 'nigeria_regions.json'

import os
def region_root_object():
    if not os.path.exists(NIGERIA_REGION_CACHE):
        load_nigeria_regions_to_file()
    f = open(NIGERIA_REGION_CACHE, 'r')
    d = json.loads(f.read())
    f.close()
    return import_region_thing_from_dict(d)

def load_nigeria_regions_to_file():
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
    dict_repr = country_region_thing.export_to_dict()
    json_val = json.dumps(dict_repr)
    f = open(NIGERIA_REGION_CACHE, 'w')
    f.write(json_val)
    f.close()