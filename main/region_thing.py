# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

class RegionThing(object):
    """
    A better name will come (maybe).
    
    This "RegionThing" class is used to cache the hierarchy of region & subregions for passing to the view.
    
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get(u"name")
        self.slug = kwargs.get(u"slug")
        self.children = []
        self.parent = None
    
    def find_child_by_slug_array(self, slugs):
        if slugs[0] == self.slug: slugs = slugs[1:]
        return self._find_child_by_slug_array(slugs)
    
    def _find_child_by_slug_array(self, slugs):
        """
        This is a temporary way to find objects by their slug/path
        """
        
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
    
    def _set_subregions(self, kids):
        """
        A manual way to set subregions for the sample data.
        Mainly used in tests.
        """
        self.children = kids
        for kid in self.children:
            kid.parent = self

    def export_to_dict(self):
        dict_vals = {u'name': self.name, u'slug': self.slug}
        if len(self.children) > 0:
            children = [c.export_to_dict() for c in self.children]
            dict_vals[u'children'] = children
        return dict_vals
    
def import_region_thing_from_dict(dict_vals):
    iname = dict_vals.get(u'name')
    islug = dict_vals.get(u'slug')
    rthing = RegionThing(name=iname, slug=islug)
    children = dict_vals.get(u'children', None)
    if children is not None:
        imported_children = [import_region_thing_from_dict(c) for c in children]
        rthing._set_subregions(imported_children)
    
    return rthing
