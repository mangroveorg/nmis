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
import widgets
import os
NIGERIA_REGION_CACHE = 'nigeria_regions.json'


@read_required()
def main(request):
    return render_to_response('index.html')


def region_navigation(request, region_path):
    context = RequestContext(request)
    # profile_root is the url root for the profiles
    # probably could use django's lookup thing for this
    context.profile_root = "/profiles/"
    country_root_object = region_root_object()
    context.stylesheets = []
    if region_path == "":
        return HttpResponseRedirect("/profiles/nigeria")
    #query country for sub sections
    region_thing_object = country_root_object.find_child_by_slug_array(region_path.split("/"))
    widget_ids, include_templates = widgets.widget_includes_by_region_level(len(region_thing_object.ancestors()))
    context.widgets = include_templates
    context.entity = region_thing_object.entity
    context.title = "NMIS Profiles: %s" % region_thing_object.name
    #what goes on behind the scenes that you don't need to edit--
    for widget_id in widget_ids:
        if hasattr(widgets, widget_id):
            context.__dict__[widget_id] = getattr(widgets, widget_id)(region_thing=region_thing_object, context=context)
        else:
            context.__dict__[widget_id] = False
    return render_to_response("region_navigation.html", context_instance=context)


def region_root_object():
    if not os.path.exists(NIGERIA_REGION_CACHE):
        load_nigeria_regions_to_file()
    with open(NIGERIA_REGION_CACHE, 'r') as f:
        d = json.loads(f.read())
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


def lgas_json(request):
    dbm = DatabaseManager(
                server=settings.MANGROVE_DATABASES['default']['SERVER'],
                database=settings.MANGROVE_DATABASES['default']['DATABASE'])
    lgas = [{'label': lga.aggregation_paths['_geo'][-1], \
             'path': "/".join([slugify(part) \
                               for part \
                               in lga.aggregation_paths['_geo'][-2:]])} \
            for lga in get_entities_by_type(dbm, 'LGA')]
    return HttpResponse(json.dumps(lgas), mimetype='application/json')
