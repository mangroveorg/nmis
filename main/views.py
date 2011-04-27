from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from mangrove.datastore.database import DatabaseManager
import mangrove.datastore.entity
import json

from main.region_thing import RegionThing, import_region_thing_from_dict

def main(request):
    return render_to_response('index.html')

def by_lga(request):
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE']
    )
    lgas = mangrove.datastore.entity.get_entities_by_type(dbm, 'LGA')
    lga_data = {}
    for lga in lgas:
        data = lga.get_all_data()
        if len(data):
            lga_data[lga] = data
    return render_to_response('mdgs/lga-data.html', {'lga_data': lga_data})

def region_navigation(request, region_path):
    context = RequestContext(request)
    
    # profile_root is the url root for the profiles
    # probably could use django's lookup thing for this
    context.profile_root = "/profiles/"
    
    usa = sample_region_root_object()
    nigeria = nigeria_region_root_object()

    if region_path == "": return HttpResponseRedirect("/profiles/usa")
    
    #query country for sub sections
    if region_path == "usa":
        region_thing_object = usa
    elif region_path == "nigeria":
        region_thing_object = nigeria
    else:
        region_thing_object = usa.find_child_by_slug_array(region_path.split("/"))
    
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

def sample_region_root_object():
    """
    This is sample data imported from json to serve as a placeholder so we can work
    on the views & navigation between sites in the hierarchy.
    """
    sample_dict = {'name' :'USA','slug' :'usa','children':[{'name' :'North West', \
                'slug' :'north_west','children':[{'children':[{'name' :'Seattle', \
                'slug':'seattle'},{'name' :'Tacoma','slug' :'tacoma'}],'name' :'Washington', \
                'slug' :'wa'}]},{'name' :'North East','slug' :'north_east','children':[{ \
                'name' :'Massachusetts','slug' :'ma','children':[{'name' :'Boston','slug' \
                :'boston'},{'name' :'Worchester','slug' :'woostah'}]}]},{'name' :'South West', \
                'slug' :'south_west','children':[{'name' :'Arizona','slug' :'az','children':[{ \
                'name' :'Page','slug' :'page'},{'name' :'Tuscon','slug' :'tuscon'}]}]}, \
                {'name' :'South East','slug' :'south_east','children':[{'name' :'Florida', \
                'slug' :'fl','children':[{'name' :'Key West','slug' :'key_west'}, \
                {'name' :'Orlando','slug' :'orlando'}]}]}]}
    
    return import_region_thing_from_dict(sample_dict)


def nigeria_region_root_object():
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE']
    )
    nigeria_entity = mangrove.datastore.entity.get_entities_by_type(dbm, 'Country')[0]
    nigeria = RegionThing(name='Nigeria', slug='nigeria')
    return nigeria
