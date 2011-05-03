"""
These methods are intended to package up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id.html

The widget_ids for each level are set in widgets.py.
"""

def _packaged_dict_for_entity(rt):
    """
    This can be reused with commonly repeated values for the widget.
    """
    entity = rt.entity
    return {u'entity_id': entity.id, \
            u'name': entity.aggregation_paths['_geo'][-1]}

def country_view(region_thing):
    d = _packaged_dict_for_entity(region_thing)
    d['marks_favorite_movie'] = "Top Gun"
    return d

def lga_view(region_thing):
    d = _packaged_dict_for_entity(region_thing)
    return d

def state_view(region_thing):
    d = _packaged_dict_for_entity(region_thing)
    return d

def mdg_table(region_thing):
    d = _packaged_dict_for_entity(region_thing)
    return d

def table_ranking(region_thing):
    return {'variable':'Child Mortality', 'list': [\
                {'name': 'First', 'color': '#A0EFA0', 'rank': '#1', 'value': '0'}, \
                {'name': 'Second', 'color': 'red', 'rank': '#2', 'value': '50'}]}

def some_metadata(region_thing):
    return {}