"""
These methods are intended to package up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id.html

The widget_ids for each level are set in widgets.py.
"""

def _packaged_dict_for_entity(entity):
    """
    This can be reused with commonly repeated values for the widget.
    """
    return {u'entity_id': entity.id, \
            u'name': entity.aggregation_paths['_geo'][-1]}

def country_view(entity, region_thing):
    d = _packaged_dict_for_entity(entity)
    return d

def lga_view(entity, region_thing):
    d = _packaged_dict_for_entity(entity)
    return d

def state_view(entity, region_thing):
    d = _packaged_dict_for_entity(entity)
    return d

def mdg_table(entity, region_thing):
    d = _packaged_dict_for_entity(entity)
    return d
