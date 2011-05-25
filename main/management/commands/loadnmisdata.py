from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from mangrove.datastore.entity import Entity


class Command(BaseCommand):
    help = "Loads the NMIS dataset from the 'NIMS Data' Google Doc."
    args = "<server> <database> | <database>"

    def handle(self, *args, **options):
        server = settings.MANGROVE_DATABASES['default']['SERVER']
        database = settings.MANGROVE_DATABASES['default']['DATABASE']
        if len(args) == 2:
            server = args[0]
            database = args[1]
        elif len(args) == 1:
            database = args[0]
        elif len(args) == 0:
            pass
        else:
            raise CommandError('Wrong number of arguments. Run \'python manage.py help loadnmisdata\' for usage.')
        #self._import_data(server, database)
        self._import_data(server, database)

    def _import_data(self, server, database):
        from mangrove.datastore.database import DatabaseManager
        from mangrove.datastore.entity import Entity, get_entities_by_value
        from mangrove.datastore.datadict import DataDictType, get_datadict_type, create_datadict_type
        from mangrove.utils import GoogleSpreadsheetsClient
        from mangrove.utils.google_spreadsheets import get_string, get_number, get_boolean, get_list
        from mangrove.utils.spreadsheets import CsvReader
        from mangrove.utils.helpers import slugify
        from mangrove.georegistry.api import get_feature_by_id
        import os
        import datetime
        import json
        from pytz import UTC

        print "Loading 'NIMS Data'..."

        print "\tServer: %s" % server
        print "\tDatabase: %s" % database

        dbm = DatabaseManager(server=server, database=database)

        user_spreadsheets = GoogleSpreadsheetsClient(settings.GMAIL_USERNAME, settings.GMAIL_PASSWORD)
        nims_data = user_spreadsheets['NIMS Data Deux']

        load_population = True
        load_other = True
        load_mdg = True
        load_health = True
        load_water = True
        load_education = True
        max_facilities_to_import = 10000

        countries = {}
        states = {}
        locations = {}
        num_cgs = 0
        datadict_types = {}
        geo_id_dict = {}

        cgs_type = create_datadict_type(
            dbm,
            slug='cgs',
            name='CGS',
            primitive_type='boolean'
        )
        datadict_types['cgs'] = cgs_type.id

        geo_id_type = create_datadict_type(
            dbm,
            slug='geo_id',
            name='Geographic ID',
            primitive_type='string'
        )
        datadict_types['geo_id'] = geo_id_type.id

        name_type = create_datadict_type(
            dbm,
            slug='name',
            name='Name',
            primitive_type='string'
        )
        datadict_types['name'] = name_type.id

        mdg_type = create_datadict_type(
            dbm,
            slug='mdg',
            name='MDG',
            primitive_type='string'
        )
        datadict_types['mdg'] = mdg_type.id

        country_geo_id = {}
        for row in nims_data['Nigeria Country ALL']:
            country_geo_id[row['name']] = row['grid']
        state_geo_ids = {}
        for row in nims_data['Nigeria States ALL']:
            state_geo_ids[row['name']] = row['grid']

        num_rows = 0
        print "Importing location entities from 'Nigeria LGAs ALL' worksheet"
        for row in nims_data['Nigeria LGAs ALL']:
            country = get_string('country', row)
            state = get_string('state', row)
            lga = get_string('lga', row)
            cgs = get_boolean('cgs', row)
            geo_id = get_string('geoid', row)
            lga_gr_id = get_string('grid', row)
            location = (country, state, lga)
            if country not in countries:
                gr_id = country_geo_id[country]
#                feature = get_feature_by_id(gr_id)
#                geometry = feature['geometry']
#                centroid = json.loads(feature['properties']['geometry_centroid'])
                e = Entity(dbm,
                           entity_type=["Location", "Country"],
                           location=[country],
#                           centroid=centroid,
                           gr_id=gr_id)
                locations[(country,)] = e.save()
                countries[country] = e.id
                data = [(name_type.slug, country, name_type)]
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                num_rows += 1
                print "[%s]...(%s) -- %s" % (num_rows, country, e.id)
            if state not in states:
                gr_id = state_geo_ids[state]
#                feature = get_feature_by_id(gr_id)
#                geometry = feature['geometry']
#                centroid = json.loads(feature['properties']['geometry_centroid'])
                e = Entity(dbm,
                           entity_type=["Location", "State"],
                           location=[country, state],
#                           centroid=centroid,
                           gr_id=gr_id)
                locations[(country, state)] = e.save()
                states[state] = e.id
                data = [(name_type.slug, state, name_type)]
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                num_rows += 1
                print "[%s]...(%s, %s) -- %s" % (num_rows, country, state, e.id)
            gr_id = lga_gr_id
#            feature = get_feature_by_id(gr_id)
#            geometry = feature['geometry']
#            centroid = json.loads(feature['properties']['geometry_centroid'])
            e = Entity(dbm,
                       entity_type=["Location", "LGA"],
                       location=[country, state, lga],
#                       centroid=centroid,
                       gr_id=gr_id)
            locations[location] = e.save()
            geo_id_dict[geo_id] = e
            data = [(name_type.slug, lga, name_type)]
            e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
            data = [(geo_id_type.slug, geo_id, geo_id_type)]
            e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))

            num_rows += 1
            print "[%s]...(%s, %s, %s) -- %s" % (num_rows, country, state, lga, e.id)
            if cgs:
                num_cgs += 1
                e.add_data(data=[(cgs_type.slug, cgs, cgs_type)])

        print "Countries (%d)" % len(countries)
        print "States (%d)" % len(states)
        print "LGAs (%d) (%d as CGS)" % ((len(locations) - len(countries) - len(states)), num_cgs)
        print "Total locations (%d)" % len(locations)

        lga_loaded = []
        lga_failed = []

        if load_population:
            print "Adding data from 'Population Data' worksheet"
            for row in nims_data['Population Variables']:
                slug = get_string('slug', row)
                name = get_string('name', row)
                primitive_type = get_string('primitivetype', row)
                tags = get_list('tags', row)
                if not slug in datadict_types:
                    dd_type = create_datadict_type(
                        dbm,
                        slug=slug,
                        name=name,
                        primitive_type=primitive_type,
                        tags=tags
                    )
                    datadict_types[slug] = dd_type.id

            for row in nims_data['Population Data']:
                state = get_string('state', row)
                lga = get_string('lga', row)
                location = ("Nigeria", state, lga)
                data = []
                if not state or not lga:
                    continue
                for dd_key in datadict_types.keys():
                    ss_key = dd_key.replace('_', '')
                    point = (dd_key, get_number(ss_key, row), get_datadict_type(dbm, datadict_types[dd_key]))
                    data.append(point)
                if location in locations:
                    lga_loaded.append(lga)
                    e = dbm.get(locations[location], Entity)
                    e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                    print [(key, value) for (key, value, typ) in data]
                else:
                    if not lga in lga_failed:
                        lga_failed.append(lga)

            print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
            if lga_failed:
                print "%d LGAs failed to load:" % len(lga_failed)
                for lga in lga_failed:
                    print "\t%s" % lga

        lga_loaded = []
        lga_failed = []
        if load_other:
            print "Adding data from 'lga_other' worksheet"
            for row in nims_data['lga_other_variables']:
                slug = get_string('slug', row)
                name = get_string('name', row)
                primitive_type = get_string('primitivetype', row)
                tags = get_list('tags', row)
                if not slug in datadict_types:
                    dd_type = create_datadict_type(
                        dbm,
                        slug=slug,
                        name=name,
                        primitive_type=primitive_type,
                        tags=tags
                    )
                    datadict_types[slug] = dd_type.id

            for row in nims_data['lga_other']:
                state = get_string('state', row)
                lga = get_string('lga', row)
                location = ("Nigeria", state, lga)
                data = []
                if not state or not lga:
                    continue
                for dd_key in datadict_types.keys():
                    ss_key = dd_key.replace('_', '')
                    if not get_number(ss_key, row): continue
                    point = (dd_key, get_number(ss_key, row), get_datadict_type(dbm, datadict_types[dd_key]))
                    data.append(point)
                if location in locations:
                    lga_loaded.append(lga)
                    e = dbm.get(locations[location], Entity)
                    e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                    print [(key, value) for (key, value, typ) in data]
                else:
                    if not lga in lga_failed:
                        lga_failed.append(lga)

            print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
            if lga_failed:
                print "%d LGAs failed to load:" % len(lga_failed)
                for lga in lga_failed:
                    print "\t%s" % lga

        if load_mdg:
            print "Adding MDG indicator data..."

            print "Adding data from 'Education MDG Data' worksheet"
            lga_loaded = []
            lga_failed = []
            for row in nims_data['Education MDG Data']:
                raw_slug = get_string('indicator', row)
                if not raw_slug: continue
                slug = str(slugify(unicode(raw_slug, 'utf-8')))
                name = get_string('indicator', row)
                lga = get_string('lga', row)
                state = get_string('state', row)
                mdg = get_string('mdg', row)
                value = get_string('value', row)
                location = ("Nigeria", state, lga)
                if not slug in datadict_types:
                    dd_type = create_datadict_type(
                        dbm,
                        slug=slug,
                        name=name,
                        primitive_type='number',
                        tags=['Education', 'MDG']
                    )
                    datadict_types[slug] = dd_type.id
                data = [(slug, value, get_datadict_type(dbm, datadict_types[slug]))]
                if location in locations:
                    lga_loaded.append(lga)
                    e = dbm.get(locations[location], Entity)
                    e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                    print [(key, value) for (key, value, typ) in data]
                else:
                    if not lga in lga_failed:
                        lga_failed.append(lga)

            print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
            if lga_failed:
                print "%d LGAs failed to load:" % len(lga_failed)
                for lga in lga_failed:
                    print "\t%s" % lga

            print "Adding data from 'Infrastructure MDG Data' worksheet"
            lga_loaded = []
            lga_failed = []
            for row in nims_data['Infrastructure MDG Data']:
                raw_slug = get_string('indicator', row)
                if not raw_slug: continue
                slug = str(slugify(unicode(raw_slug, 'utf-8')))
                name = get_string('indicator', row)
                lga = get_string('lga', row)
                state = get_string('state', row)
                mdg = get_string('mdg', row)
                value = get_string('value', row)
                location = ("Nigeria", state, lga)
                if not slug in datadict_types:
                    dd_type = create_datadict_type(
                        dbm,
                        slug=slug,
                        name=name,
                        primitive_type='number',
                        tags=['Infrastructure', 'MDG']
                    )
                    datadict_types[slug] = dd_type.id
                data = [(slug, value, get_datadict_type(dbm, datadict_types[slug]))]
                if location in locations:
                    lga_loaded.append(lga)
                    e = dbm.get(locations[location], Entity)
                    e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                    print [(key, value) for (key, value, typ) in data]
                else:
                    if not lga in lga_failed:
                        lga_failed.append(lga)

            print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
            if lga_failed:
                print "%d LGAs failed to load:" % len(lga_failed)
                for lga in lga_failed:
                    print "\t%s" % lga

            print "Adding data from 'Health MDG Data' worksheet"
            lga_loaded = []
            lga_failed = []
            for row in nims_data['Health MDG Data']:
                raw_slug = get_string('indicator', row)
                if not raw_slug: continue
                slug = str(slugify(unicode(raw_slug, 'utf-8')))
                name = get_string('indicator', row)
                lga = get_string('lga', row)
                state = get_string('state', row)
                mdg = get_string('mdg', row)
                value = get_string('value', row)
                location = ("Nigeria", state, lga)
                if not slug in datadict_types:
                    dd_type = create_datadict_type(
                        dbm,
                        slug=slug,
                        name=name,
                        primitive_type='number',
                        tags=['Health', 'MDG']
                    )
                    datadict_types[slug] = dd_type.id
                data = [(slug, value, get_datadict_type(dbm, datadict_types[slug]))]
                if location in locations:
                    lga_loaded.append(lga)
                    e = dbm.get(locations[location], Entity)
                    e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                    print [(key, value) for (key, value, typ) in data]
                else:
                    if not lga in lga_failed:
                        lga_failed.append(lga)

            print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
            if lga_failed:
                print "%d LGAs failed to load:" % len(lga_failed)
                for lga in lga_failed:
                    print "\t%s" % lga

        if load_health:
            print "Adding Facility data..."

            print "Adding Health Clinics and associated data"

            file_name = 'health.csv'
            dirname = settings.DATA_DIRECTORY
            abspath = os.path.abspath(dirname)
            file_path = os.path.join(abspath, file_name)
            csv_reader = CsvReader(file_path)
            num_rows = 0
            things_to_build = []
            for row in csv_reader.iter_dicts():
                num_rows += 1
                if num_rows > max_facilities_to_import:
                    break
                geo_id = get_string('geoid', row)
                geocode = get_string('geocodeoffacility', row).split()
                lat, long = None, None
                if geocode and len(geocode) >= 2:
                    lat = float(geocode[0])
                    long = float(geocode[1])
                else:
                    geocode = False
#                entities = get_entities_by_value(dbm, geo_id_type, geo_id)
#                entity = entities[0] if entities else None
                if geo_id in geo_id_dict:
                    entity = geo_id_dict[geo_id]
                else:
                    entity = False
                if entity:
                    entity_data = {}
                    entity_data['datarecords'] = []
                    if geocode:
                        entity_data['geometry'] = {'type': 'Point', 'coordinates': [lat, long]}
                    else:
                        entity_data['geometry'] = False
                    for key in row.keys():
                        slug = str(slugify(unicode(key.strip(), 'utf-8')))
                        name = key
                        primitive_type = 'string'
                        tags = ['Facility', 'Baseline', 'Health']
                        value = row[key]
                        data = {
                            'label': slug,
                            'value': value,
                            'slug': slug
                        }
                        datarecord = {
                            'slug': slug,
                            'name': name,
                            'primitive_type': primitive_type,
                            'tags': tags,
                            'value': value,
                            'data': data
                        }
                        entity_data['datarecords'].append(datarecord)
                    things_to_build.append((entity, entity_data))

            num_rows = 0
            for (e, t) in things_to_build:
                num_rows += 1
                print '[%s] Facility added inside %s' % (num_rows, e.location_path)
                if t['geometry']:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "Health Clinic"],
                                    location=e.location_path,
                                    geometry=t['geometry'])
                    print '[X]...with geometry: %s' % t['geometry']
                else:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "Health Clinic"],
                                    location=e.location_path)
                clinic.save()
                all_records = []
                for d in t['datarecords']:
                    if not d['slug'] in datadict_types:
                        dd_type = create_datadict_type(
                            dbm,
                            slug=d['slug'],
                            name=d['name'],
                            primitive_type=d['primitive_type'],
                            tags=d['tags']
                        )
                        datadict_types[d['slug']] = dd_type.id
                    data_to_add = (
                        d['data']['label'],
                        d['data']['value'],
                        get_datadict_type(dbm, datadict_types[d['slug']]))
                    all_records.append(data_to_add)
                    clinic.add_data([data_to_add])
#                clinic.add_data(all_records, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
#                print '[X]...Record added (%s variables)' % len(all_records)
                print '[X]...%s records added' % len(all_records)

            print "Loaded %d records" % num_rows

        if load_water:
            print "Adding Water Points and associated data"

            file_name = 'water.csv'
            dirname = settings.DATA_DIRECTORY
            abspath = os.path.abspath(dirname)
            file_path = os.path.join(abspath, file_name)
            csv_reader = CsvReader(file_path)
            num_rows = 0
            things_to_build = []
            for row in csv_reader.iter_dicts():
                num_rows += 1
                if num_rows > max_facilities_to_import:
                    break
                geo_id = get_string('geo_id', row)
                geocode = get_string('gps', row).split()
                lat, long = None, None
                if geocode and len(geocode) >= 2:
                    lat = float(geocode[0])
                    long = float(geocode[1])
                else:
                    geocode = False
#                entities = get_entities_by_value(dbm, geo_id_type, geo_id)
#                entity = entities[0] if entities else None
                if geo_id in geo_id_dict:
                    entity = geo_id_dict[geo_id]
                else:
                    entity = False
                if entity:
                    entity_data = {}
                    entity_data['datarecords'] = []
                    if geocode:
                        entity_data['geometry'] = {'type': 'Point', 'coordinates': [lat, long]}
                    else:
                        entity_data['geometry'] = False
                    for key in row.keys():
                        slug = str(slugify(unicode(key.strip(), 'utf-8')))
                        name = key
                        primitive_type = 'string'
                        tags = ['Facility', 'Baseline', 'Water']
                        value = row[key]
                        data = {
                            'label': slug,
                            'value': value,
                            'slug': slug
                        }
                        datarecord = {
                            'slug': slug,
                            'name': name,
                            'primitive_type': primitive_type,
                            'tags': tags,
                            'value': value,
                            'data': data
                        }
                        entity_data['datarecords'].append(datarecord)
                    things_to_build.append((entity, entity_data))

            num_rows = 0
            for (e, t) in things_to_build:
                num_rows += 1
                print '[%s] Facility added inside %s' % (num_rows, e.location_path)
                if t['geometry']:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "Water Point"],
                                    location=e.location_path,
                                    geometry=t['geometry'])
                    print '[X]...with geometry: %s' % t['geometry']
                else:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "Water Point"],
                                    location=e.location_path)
                clinic.save()
                all_records = []
                for d in t['datarecords']:
                    if not d['slug'] in datadict_types:
                        dd_type = create_datadict_type(
                            dbm,
                            slug=d['slug'],
                            name=d['name'],
                            primitive_type=d['primitive_type'],
                            tags=d['tags']
                        )
                        datadict_types[d['slug']] = dd_type.id
                    data_to_add = (
                        d['data']['label'],
                        d['data']['value'],
                        get_datadict_type(dbm, datadict_types[d['slug']]))
                    all_records.append(data_to_add)
                clinic.add_data(all_records, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                print '[X]...Record added (%s variables)' % len(all_records)

            print "Loaded %d records" % num_rows

        if load_education:
            print "Adding Education Facilities and associated data"

            file_name = 'education.csv'
            dirname = settings.DATA_DIRECTORY
            abspath = os.path.abspath(dirname)
            file_path = os.path.join(abspath, file_name)
            csv_reader = CsvReader(file_path)
            num_rows = 0
            things_to_build = []
            for row in csv_reader.iter_dicts():
                num_rows += 1
                if num_rows > max_facilities_to_import:
                    break
                geo_id = get_string('geo_id', row)
                geocode = get_string('gps', row).split()
                lat, long = None, None
                if geocode and len(geocode) >= 2:
                    lat = float(geocode[0])
                    long = float(geocode[1])
                else:
                    geocode = False
#                entities = get_entities_by_value(dbm, geo_id_type, geo_id)
#                entity = entities[0] if entities else None
                if geo_id in geo_id_dict:
                    entity = geo_id_dict[geo_id]
                else:
                    entity = False
                if entity:
                    entity_data = {}
                    entity_data['datarecords'] = []
                    if geocode:
                        entity_data['geometry'] = {'type': 'Point', 'coordinates': [lat, long]}
                    else:
                        entity_data['geometry'] = False
                    for key in row.keys():
                        slug = str(slugify(unicode(key.strip(), 'utf-8')))
                        name = key
                        primitive_type = 'string'
                        tags = ['Facility', 'Baseline', 'Education']
                        value = row[key]
                        data = {
                            'label': slug,
                            'value': value,
                            'slug': slug
                        }
                        datarecord = {
                            'slug': slug,
                            'name': name,
                            'primitive_type': primitive_type,
                            'tags': tags,
                            'value': value,
                            'data': data
                        }
                        entity_data['datarecords'].append(datarecord)
                    things_to_build.append((entity, entity_data))

            num_rows = 0
            for (e, t) in things_to_build:
                num_rows += 1
                print '[%s] Facility added inside %s' % (num_rows, e.location_path)
                if t['geometry']:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "School"],
                                    location=e.location_path,
                                    geometry=t['geometry'])
                    print '[X]...with geometry: %s' % t['geometry']
                else:
                    clinic = Entity(dbm,
                                    entity_type=["Facility", "School"],
                                    location=e.location_path)
                clinic.save()
                all_records = []
                for d in t['datarecords']:
                    if not d['slug'] in datadict_types:
                        dd_type = create_datadict_type(
                            dbm,
                            slug=d['slug'],
                            name=d['name'],
                            primitive_type=d['primitive_type'],
                            tags=d['tags']
                        )
                        datadict_types[d['slug']] = dd_type.id
                    data_to_add = (
                        d['data']['label'],
                        d['data']['value'],
                        get_datadict_type(dbm, datadict_types[d['slug']]))
                    all_records.append(data_to_add)
                clinic.add_data(all_records, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
                print '[X]...Record added (%s variables)' % len(all_records)

            print "Loaded %d records" % num_rows