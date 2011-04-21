from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from mangrove.datastore.database import DatabaseManager
import mangrove.datastore.entity

from main.region_thing import RegionThing

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
    
    if region_path == "": return HttpResponseRedirect("/profiles/usa")
    
    #query country for sub sections
    if region_path =="usa":
        region_thing_object = usa
    else:
        region_thing_object = usa.find_child_by_slug_array(region_path.split("/"))
    
    sample_dict = region_thing_object.to_dict()
    context.region_hierarchy = region_thing_object.context_dict(2)
    return render_to_response("region_navigation.html", context_instance=context)


def sample_region_root_object():
    usa = RegionThing(name="USA", slug="usa")
    
    nw = RegionThing(name="North West", slug="north_west")
    nw_state = RegionThing(name="Washington", slug="wa")
    wa1 = RegionThing(name="Seattle", slug="seattle")
    wa2 = RegionThing(name="Tacoma", slug="tacoma")
    nw_state._set_subregions([wa1, wa2])
    nw._set_subregions([nw_state])
    
    ne = RegionThing(name="North East", slug="north_east")
    ne_state = RegionThing(name="Massachusetts", slug="ma")
    ma1 = RegionThing(name="Boston", slug="boston")
    ma2 = RegionThing(name="Worchester", slug="woostah")
    ne_state._set_subregions([ma1, ma2])
    ne._set_subregions([ne_state])

    sw = RegionThing(name="South West", slug="south_west")
    sw_state = RegionThing(name="Arizona", slug="az")
    az1 = RegionThing(name="Page", slug="page")
    az2 = RegionThing(name="Tuscon", slug="tuscon")
    sw_state._set_subregions([az1, az2])
    sw._set_subregions([sw_state])
    
    se = RegionThing(name="South East", slug="south_east")
    se_state = RegionThing(name="Florida", slug="fl")
    fl1 = RegionThing(name="Key West", slug="key_west")
    fl2 = RegionThing(name="Orlando", slug="orlando")
    se_state._set_subregions([fl1, fl2])
    se._set_subregions([se_state])
    
    usa._set_subregions([nw, ne, sw, se])
    return usa