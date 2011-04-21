from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from mangrove.datastore.database import DatabaseManager
import mangrove.datastore.entity

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

import json

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
        region_thing_object = usa._find_child_by_slug_array(region_path.split("/"))
    
    sample_dict = region_thing_object.to_dict()
    context.region_hierarchy = region_thing_object.context_dict(2)
    return render_to_response("region_navigation.html", context_instance=context)

class RegionThing(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get(u"name")
        self.slug = kwargs.get(u"slug")
        self.children = []
        self.parent = None
    
    def _find_child_by_slug_array(self, slugs):
        """
        This is a temporary way to find objects by their slug/path
        """
        
        if slugs[0] == self.slug: slugs = slugs[1:]
        
        next_child = False
        for c in self.children:
            if c.slug == slugs[0]:
                next_child = c
                break
        
        if len(slugs) > 1: return next_child._find_child_by_slug_array(slugs[1:])
        
        return next_child
    
    def info_dict(self):
        return {'name': self.name, 'slug': self.slug, 'path': self.path()}
    
    def context_dict(self, depth=2):
        d = self.to_dict(depth)
        ancestors = self.ancestors()
        ancestors.reverse()
        parent_info = [p.info_dict() for p in ancestors]
        d['level'] = len(parent_info)
        d['parents'] = parent_info
        d['path'] = self.path()
        return d
    
    def to_dict(self, depth=2):
        if depth < 1:
            return self.info_dict()
        
        my_data = self.info_dict()
        child_depth = depth-1
        my_data['children'] = [c.to_dict(child_depth) for c in self.children]
        return my_data
    
    def ancestors(self):
        _ancestors = []
        pt = self.parent
        while pt is not None:
            _ancestors.append(pt)
            pt = pt.parent
        return _ancestors
    
    def path(self):
        a = self.ancestors()
        a.reverse()
        slugs = [s.slug for s in a]
        slugs.append(self.slug)
        return "/".join(slugs)
    
    def _parent_data(self):
        return [p.info_dict() for p in self.ancestors()]
    
    def _set_subregions(self, kids):
        """
        a manual way to set subregions for the sample data
        """
        self.children = kids
        for kid in self.children:
            kid.parent = self

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