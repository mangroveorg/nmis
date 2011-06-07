"""
These methods are intended to package up a dict which is passed to the template in BASE_TEMPLATES/widgets/widget_id.html

The widget_ids for each level are set in widgets.py.
"""
import json

from django.conf import settings
from mangrove.datastore.database import DatabaseManager, get_db_manager
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
        value = get_variable_values_for_region_thing(i['slug'], region_thing)
	tt = {'value': value,\
              'goal_number': i['goal_number'],\
              'sector': i['sector'],\
              'subsector': i['subsector'],\
              'name': i['name'],\
              'data_source': i['data_source']}
        if i['lga_display'] and value is not None:
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


class TableBuilder(object):

    def __init__(self, sector, headers, region_thing):
        self._set_sector(sector)
        self._set_headers(headers)
        self._set_region_thing(region_thing)

    def _set_sector(self, sector):
        self._sector = sector

    def _set_headers(self, headers):
        assert type(headers) == list
        for header in headers:
            assert type(header)==list and len(header) == 2
        self._headers = headers

    def _set_region_thing(self, region_thing):
        self._region_thing = region_thing

    def get_data_for_table(self):
        """
        Return a list of cells for inclusion in this table. Base these cells on the sector, headers,
        and region thing of this table builder.
        """
        dbm = get_db_manager(
            server=settings.MANGROVE_DATABASES['default']['SERVER'],
            database=settings.MANGROVE_DATABASES['default']['DATABASE'])
        facilities = get_entities_in(dbm, self._region_thing.entity.location_path, self._sector)
        slugs = [header[0] for header in self._headers]
        result = []
        for facility in facilities:
            d = {
                'sector': self._sector,
                'facility_type': self._sector,
                'latlng': facility.geometry['coordinates'],
                'img_id': facility.value('photo')
            }
            for k in slugs:
                d[k] = facility.value(k)
            result.append(d)
        return result


def lga_facilities_data(region_thing, context):
    tables = {
        'Health Clinic': [
            ['facility_name', 'Name'],
            ['facility_type', 'Type'],
            ['power_sources_none', 'No Power Source'],
            ['facility_owner_manager', 'Owner/Manager'],
            ['all_weather_road_yn', 'All-weather Road'],
            ['health_facility_condition', 'Condition']
        ],
        'School': [
            ['school_name', 'Name'],
            ['level_of_education', 'Level of Education'],
            ['education_type', 'Education Type'],
            ['all_weather_road_yn', 'All-weather Road'],
            ['power_sources_none', 'No Power Source'],
            ['water_sources_none', 'No Water Source']
        ],
        'Water Point': [
            ['water_source_type', 'Type'],
            ['lift', 'Lift'],
            ['water_source_developed_by', 'Developed by'],
            ['water_source_used_today_yn', 'Used today'],
            ['water_source_physical_state', 'Physical State']
        ]
        }
    sector_list = []
    facility_data = []
    for sector, headers in tables.items():
        d = {
            'slug': sector,
            'name': sector + 's',
            'columns': headers
        }
        sector_list.append(d)
        table_builder = TableBuilder(sector, headers, region_thing)
        data = table_builder.get_data_for_table()
        print data
        facility_data.extend(data)
    context.facility_data = json.dumps(facility_data, indent=4)
    context.facility_sectors = json.dumps(sector_list)


def lga_facilities_table(region_thing, context):
    context.facilities_list = [region_thing.name]


def lga_map(region_thing, context):
    ll = [6.4530,3.3958333]
#    ll = region_thing.entity.centroid
    context.lga_centroid = ll
