"""
This packages up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id

The widget_ids for each level are set in widgets.py
"""

def country_view(entity):
    return {u'entity_id': entity.id,
            u'name': entity.aggregation_paths['_geo'][-1]}

def lga_view(entity):
    return {u'entity_id': entity.id,
            u'name': entity.aggregation_paths['_geo'][-1]}

def state_view(entity):
    return {u'entity_id': entity.id,
            u'name': entity.aggregation_paths['_geo'][-1]}

def mdg_table(entity):
    return {u'entity_id': entity.id,
            u'name': entity.aggregation_paths['_geo'][-1]}
