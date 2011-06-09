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
        self._headers = []
        for slug in headers:
            data_dict_type = DataDictType.get_type(slug)
            self._headers.append(data_dict_type)

    def _set_region_thing(self, region_thing):
        self._region_thing = region_thing

    def get_headers_for_table(self):
        return [{
            'slug': ddt.slug,
            'name': ddt.name
        } for ddt in self._headers]

    def _fix_values(self, d):
        def is_float(v):
            try:
                float(v)
                return True
            except:
                return False
        def is_boolean(v):
            return v in [u"TRUE", u"FALSE"]
        import datetime
        for k, v in d.items():
            if is_float(v):
                d[k] = float(v)
            elif is_boolean(v):
                d[k] = v == u"TRUE"
            elif isinstance(v, datetime.datetime):
                pass
            else:
                # this is a string
                d[k] = v.title().replace("_", " ")
                

    def _add_calculated_sector_indicators(self, d):
        self._fix_values(d)
        if self._sector == 'health':
            pass
        elif self._sector == 'education':
            self._add_student_teacher_ratio(d)
            self._add_sufficient_number_of_classrooms(d)
        elif self._sector == 'water':
            pass

    def _add_student_teacher_ratio(self, d):
        d['student_teacher_ratio'] = int(d['num_students_total'] / max(d['num_tchrs_total'], 0.001))
        d['student_teacher_ratio_ok'] = d['student_teacher_ratio'] <= 35

    def _add_sufficient_number_of_classrooms(self, d):
        d['ideal_number_of_classrooms'] = int(d['num_students_total'] / 35)
        d['total_number_of_classrooms'] = d['num_classrms_good_cond'] + d['num_classrms_need_min_repairs'] + d['num_classrms_need_maj_repairs']
        d['sufficient_number_of_classrooms'] = d['total_number_of_classrooms'] >= d['ideal_number_of_classrooms']
        d['percentage_of_classrooms_in_good_condition'] = int(d['num_classrms_good_cond'] / max(d['total_number_of_classrooms'], 0.001) * 100.0)

    def get_data_for_table(self):
        """
        Return a list of cells for inclusion in this table. Base these cells on the sector, headers,
        and region thing of this table builder.
        """
        dbm = get_db_manager(
            server=settings.MANGROVE_DATABASES['default']['SERVER'],
            database=settings.MANGROVE_DATABASES['default']['DATABASE'])
        sector_to_facility = {
            'health': 'Health Clinic',
            'education': 'School',
            'water': 'Water Point'
        }
        facility_type = sector_to_facility[self._sector]
        facilities = get_entities_in(dbm, self._region_thing.entity.location_path, facility_type)
        slugs = [header.slug for header in self._headers]
        result = []
        for facility in facilities:
            data = facility.get_all_data()
            times = data.keys()
            times.sort()
            # get the latest data
            latest_data = data[times[-1]]
            self._add_calculated_sector_indicators(latest_data)
            d = dict([(slug, latest_data[slug]) for slug in slugs])
            d.update(
                {
                    'sector': self._sector,
                    'facility_type': facility_type,
                    'latlng': facility.geometry['coordinates'],
                    'img_id': latest_data['photo']
                    }
                )
            result.append(d)
        return result

class DataDictType(object):
    FIELDS = ['slug', 'name', 'description']

    TYPES = [
        ['facility_name', 'Name', 'This is the facility name, bitch!'],
        ['facility_type', 'Type'],
        ['power_sources_none', 'No Power Source', "There ain't no power source at this god forsaken facility."],
        ['facility_owner_manager', 'Owner/Manager'],
        ['all_weather_road_yn', 'All-weather Road'],
        ['health_facility_condition', 'Condition'],
        ['school_name', 'Name'],
        ['level_of_education', 'Level of Education'],
        ['education_type', 'Education Type'],
        ['all_weather_road_yn', 'All-weather Road'],
        ['power_sources_none', 'No Power Source'],
        ['water_sources_none', 'No Water Source'],
        ['water_source_type', 'Type'],
        ['lift', 'Lift'],
        ['water_source_developed_by', 'Developed by'],
        ['water_source_used_today_yn', 'Used today'],
        ['water_source_physical_state', 'Physical State'],
        ['student_teacher_ratio', 'Student/Teacher Ratio'],
        ['student_teacher_ratio_ok', 'Student/Teacher Ratio OK'],
        ['ideal_number_of_classrooms', 'Ideal # of Classrooms'],
        ['total_number_of_classrooms', 'Total # of Classrooms'],
        ['sufficient_number_of_classrooms', 'Sufficient # of Classrooms'],
        ['percentage_of_classrooms_in_good_condition', '% of Classrooms in Good Condition']       
    ]

    def __init__(self, *args):
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)
        # **kwargs
        # for field in self.FIELDS:
        #     setattr(self, field, kwargs.get(field))


    @classmethod
    def _create_types(cls):
        cls._types = {}
        for args in cls.TYPES:
            cls._types[args[0]] = DataDictType(*args)

    @classmethod
    def get_type(cls, slug):
        if not hasattr(cls, '_types'):
            cls._create_types()
        return cls._types[slug]


def lga_facilities_data(region_thing, context):
    tables = {
        'health': [
            'facility_name',
            'facility_type',
            'power_sources_none',
            'facility_owner_manager',
            'all_weather_road_yn',
            'health_facility_condition',
        ],
        'education': [
            'school_name',
            # 'level_of_education',
            # 'education_type',
            'power_sources_none',
            'water_sources_none',
            'student_teacher_ratio',
            'student_teacher_ratio_ok',
            'ideal_number_of_classrooms',
            'total_number_of_classrooms',
            'sufficient_number_of_classrooms',
            'percentage_of_classrooms_in_good_condition'
        ],
        'water': [
            'water_source_type',
            'lift',
            'water_source_developed_by',
            'water_source_used_today_yn',
            'water_source_physical_state',
        ]
    }
    sector_list = []
    facility_data = []
    for sector, slugs in tables.items():
        table_builder = TableBuilder(sector, slugs, region_thing)
        data = table_builder.get_data_for_table()
        facility_data.extend(data)
        headers = table_builder.get_headers_for_table()
        sector_list.append({
            'slug': sector,
            'name': sector.capitalize(),
            'columns': headers
        })
    context.facility_table_data = json.dumps({\
        'data': facility_data,
        'sectors': sector_list
    })

def lga_facilities_table(region_thing, context):
    context.facilities_list = [region_thing.name]


def lga_map(region_thing, context):
    #ll = [6.4530,3.3958333]
    ll = region_thing.entity.centroid
    context.lga_centroid = ll
