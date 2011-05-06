"""
These methods are intended to package up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id.html

The widget_ids for each level are set in widgets.py.
"""
import json


def _packaged_dict_for_entity(rt):
    """
    This can be reused with commonly repeated values for the widget.
    """
    entity = rt.entity
    return {u'entity_id': entity.id, \
            u'name': entity.aggregation_paths['_geo'][-1]}


def lga_view(region_thing, context):
    d = _packaged_dict_for_entity(region_thing)
    return d


def state_map(region_thing, context):
    pass


def state_mdg_performance(region_thing, context):
    pass


def mdg_table(region_thing, context):
    d = _packaged_dict_for_entity(region_thing)
    mdg_data = {}
    mdg_data['years'] = [2011]
    mdg_data['variables'] = {}
    e = region_thing.entity
    data_types_by_slug = dict([(t.slug, t) for t in e.data_types(['MDG'])])
    values_by_slug = e.values(dict([(k, 'latest') for k in data_types_by_slug.keys()]))
    for slug, val in values_by_slug.items():
        mdg = data_types_by_slug[slug]._doc['mdg'].split('.')
        goal, subgoal = None, None
        if len(mdg) == 2:
            goal = mdg[0]
            subgoal = mdg[1]
        elif len(mdg) == 1:
            goal = mdg[0]
        mdg_data['variables'][slug] = {
            'name': data_types_by_slug[slug].name,
            'data_type': data_types_by_slug[slug].primitive_type,
            'display_order': 0,
            'values': {
                '2011': val
            },
            'goal': goal
        }
        if subgoal is not None:
            mdg_data['variables'][slug]['subgoal'] = subgoal
    d['mdg_data'] = json.dumps(mdg_data)
    return d

def country_map(region_thing, context):
    pass

def country_state_nav(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)

def table_ranking(region_thing, context):
    return {'variable': 'Child Mortality', 'list': [\
                {'name': 'First', 'color': '#A0EFA0', 'rank': '#1', 'value': '0'}, \
                {'name': 'Second', 'color': 'red', 'rank': '#2', 'value': '50'}]}

def regnav_country(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)

def regnav_state(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)

def regnav_lga(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)
    context.state_ro = region_thing.parent
    context.lga_siblings = region_thing.parent.children

def some_metadata(region_thing, context):
    return {}
