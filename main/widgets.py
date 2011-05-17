"""
These methods are intended to package up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id.html

The widget_ids for each level are set in widgets.py.
"""
import json

from django.conf import settings
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import get_entities_by_type, get_entities_in

WIDGETS_BY_REGION_LEVEL = [
        #country:
        ["country_map", "country_key_indicators", "country_state_nav"],
        #state:
        ["regnav_state", "state_map", "state_mdg_performance"],
        #lga:
        ["regnav_lga", "lga_facilities_data", "lga_map", "lga_mdg_table", "lga_facilities_table"]
]


def widget_includes_by_region_level(rl=0):
    widgets = WIDGETS_BY_REGION_LEVEL[rl]
    include_templates = ["widgets/%s.html" % w for w in widgets]
    return (widgets, include_templates)


def _packaged_dict_for_entity(rt):
    """
    This can be reused with commonly repeated values for the widget.
    """
    entity = rt.entity
    return {u'entity_id': entity.id,\
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
                {'name': 'First', 'color': '#A0EFA0', 'rank': '#1', 'value': '0'},\
                {'name': 'Second', 'color': 'red', 'rank': '#2', 'value': '50'}]}


def regnav_country(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)


def regnav_state(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)


def regnav_lga(region_thing, context):
    context.region_hierarchy = region_thing.context_dict(2)
    context.state_ro = region_thing.parent
    context.lga_siblings = region_thing.parent.children


from main.raw_mdg_indicator_list import INDICATORS as indicator_list
from collections import defaultdict


def format_indicator(value):
    try:
        fvalue = float(value)
        return "%.2f" % fvalue
    except:
        pass
    return value


def get_variable_values_for_region_thing(variable_slug, region_thing, data_set={}):
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE'])
    #print("ENTITY: %s -- %s" % (region_thing.entity, region_thing.entity.id))
    #print("SLUG: %s" % variable_slug)
    return format_indicator(region_thing.entity.values({variable_slug: 'latest'})[variable_slug])


def lga_mdg_table(region_thing, context):
    context.stylesheets.append('/static/css/src/mdg_table.css')
    sector_names = []
    sector_grouped_data = {}
    for i in indicator_list:
        sname = i['sector']
        sslug = sname.lower()
        if sname not in sector_names:
            sector_names.append(sname)
            sector_grouped_data[sslug] = []
        tt = {'value': get_variable_values_for_region_thing(i['slug'], region_thing),\
              'goal_number': i['goal_number'],\
              'sector': i['sector'],\
              'subsector': i['subsector'],\
              'name': i['name'],\
              'data_source': i['data_source']}
        if i['lga_display']:
            sector_grouped_data[sslug].append(tt)
    sectors = []
    for s in sector_names:
        sectors.append({'name': s, 'slug': s.lower()})
    context.indicator_list = {'sectors': sectors, 'grouped_list': sector_grouped_data,
                              'grouped_list_json': json.dumps(sector_grouped_data)}


def get_score_for(facility, slug):
    raw_score = facility.values({slug: 'latest'})[slug]
    if not raw_score:
        raw_score = 0
        #print("SCORE:%s" % raw_score)
    try:
        f = float(raw_score)
        p = f * 100
        score = "%.2f" % p + "%"
        return score
    except Exception as e:
        #print("EXCP: %s" % e)
        pass
    return raw_score


def lga_facilities_data(region_thing, context):
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE'])

    try:
        entities_list = get_entities_in(dbm, region_thing.entity.location_path, 'Health Clinic')
        #print("\n".join([e.id for e in entities_list]))
        facility_list = [{'sector': 'health',\
                          'id': hc.id,\
                          'facility_type': hc.values({'facility_name': 'latest'})['facility_name'].title(),\
                          'access_pct': get_score_for(hc, 'access'),\
                          'infrastructure_pct': get_score_for(hc, 'infrastructure'),\
                          'staffing_pct': get_score_for(hc, 'staffing'),\
                          'hiv_pct': get_score_for(hc, 'hiv_services'),\
                          'maternal_pct': get_score_for(hc, 'maternal_services'),\
                          'supplies_pct': get_score_for(hc, 'equipment_supplies'),\
                          'latlng': '%s' % hc.geometry['coordinates'][0] + ',' + '%s' % hc.geometry['coordinates'][1],\
                          'image_id': hc.values({'photo': 'latest'})['photo'][:-4]}\
                         for hc in entities_list]
    except Exception as e:
        #print("ERROR: %s" % e)
        pass

    #f1 = {'sector': 'health', 'facility_type': 'Primary Health Post', 'access_pct': "70%", 'infrastructure_pct': "30%", 'staffing_pct': "13%", 'hiv_pct': "5%", 'maternal_pct': "16%", 'supplies_pct': "53%", 'latlng': '7.631101,8.539607', 'image_id': '11223342'}
    #f2 = {'sector': 'health', 'facility_type': 'Primary Health Post', 'access_pct': "70%", 'infrastructure_pct': "30%", 'staffing_pct': "20%", 'hiv_pct': "10%", 'maternal_pct': "59%", 'supplies_pct': "43%", 'latlng': '7.531101,8.539607', 'image_id': '11223343'}
    #f3 = {'sector': 'education', 'facility_type': 'School', 'latlng': '7.631101,8.639607', 'image_id': '11223344'}
    #f4 = {'sector': 'water', 'facility_type': 'Water Point', 'latlng': '7.531101,8.639607', 'image_id': '11223345'}

    #facility_list = [f1, f2, f3, f4]

    health_columns = [['facility_type', 'Facility Type'],
                      ['access_pct', 'Access'],
                      ['infrastructure_pct', 'Infrastructure'],
                      ['staffing_pct', 'Staffing'],
                      ['hiv_pct', 'HIV'],
                      ['maternal_pct', 'Maternal'],
                      ['supplies_pct', 'Supplies']]
    edu_columns = [['facility_type', 'Facility Type']]
    water_columns = [['facility_type', 'Facility Type']]

    sector_list = [{'slug': 'health', 'name': 'Health', 'columns': health_columns},
                   #      {'slug': 'education', 'name': 'Education', 'columns': edu_columns},
                   #      {'slug': 'water', 'name': 'Water', 'columns': water_columns}
    ]

    context.facility_data = json.dumps(facility_list)
    context.facility_sectors = json.dumps(sector_list)


def lga_facilities_table(region_thing, context):
    context.facilities_list = [region_thing.name]
