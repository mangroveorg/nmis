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
        self._import_data(server, database)

    def _import_data(self, server, database):
        from mangrove.datastore.database import DatabaseManager
        from mangrove.datastore.entity import Entity
        from mangrove.datastore.datadict import DataDictType, get_datadict_type
        import mangrove.datastore.entity
        from mangrove.utils import GoogleSpreadsheetsClient
        from mangrove.utils.google_spreadsheets import get_string, get_number, get_percent, get_boolean, get_list
        from mangrove.utils.helpers import slugify
        import datetime
        from pytz import UTC

        print "Loading 'NIMS Data'..."

        print "\tServer: %s" % server
        print "\tDatabase: %s" % database

        dbm = DatabaseManager(server=server, database=database)

        user_spreadsheets = GoogleSpreadsheetsClient(settings.GMAIL_USERNAME, settings.GMAIL_PASSWORD)
        nims_data = user_spreadsheets['NIMS Data Deux']

        countries = {}
        states = {}
        locations = {}
        num_cgs = 0
        datadict_types = {}
        cgs_type = DataDictType(
            dbm,
            slug='cgs',
            name='CGS',
            primitive_type='boolean'
        )
        datadict_types['cgs'] = cgs_type.save()

        print "Importing location entities from 'Nigeria LGAs ALL' worksheet"
        for row in nims_data['Nigeria LGAs ALL']:
            country = get_string('country', row)
            state = get_string('state', row)
            lga = get_string('lga', row)
            cgs = get_boolean('cgs', row)
            location = (country, state, lga)
            if country not in countries:
                e = Entity(dbm, entity_type=["Location", "Country"], location=[country])
                locations[(country)] = e.save()
                countries[country] = e.id
                print "...(%s)" % country
            if state not in states:
                e = Entity(dbm, entity_type=["Location", "State"], location=[country, state])
                locations[(country, state)] = e.save()
                states[state] = e.id
                print "...(%s, %s)" % (country, state)
            e = Entity(dbm, entity_type=["Location", "LGA"], location=[country, state, lga])
            locations[location] = e.save()
            print "...(%s, %s, %s)" % location
            if cgs:
                num_cgs += 1
                e.add_data(data=[(cgs_type.slug, cgs, cgs_type)])

        print "Countries (%d)" % len(countries)
        print "States (%d)" % len(states)
        print "LGAs (%d) (%d as CGS)" % ((len(locations) - len(countries) - len(states)), num_cgs)
        print "Total locations (%d)" % len(locations)
        print "Adding data from 'Population Data' worksheet"
        lga_loaded = []
        lga_failed = []

        for row in nims_data['Population Variables']:
            slug = get_string('slug', row)
            name = get_string('name', row)
            primitive_type = get_string('primitivetype', row)
            tags = get_list('tags', row)
            if not slug in datadict_types:
                dd_type = DataDictType(
                    dbm,
                    slug=slug,
                    name=name,
                    primitive_type=primitive_type,
                    tags=tags
                )
                datadict_types[slug] = dd_type.save()

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
            else:
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
        if lga_failed:
            print "%d LGAs failed to load:" % len(lga_failed)
            for lga in lga_failed:
                print "\t%s" % lga
        print "Adding MDG indicator data..."

        print "Adding data from 'Education MDG Data' worksheet"
        lga_loaded = []
        lga_failed = []
        for row in nims_data['Education MDG Data']:
            slug = str(slugify(unicode(row['indicator'].strip(), 'utf-8')))
            name = row['indicator'].strip()
            lga = row['lga'].strip()
            state = row['state'].strip()
            mdg = row['mdg'].strip()
            location = ("Nigeria", state, lga)
            if not slug in datadict_types:
                dd_type = DataDictType(
                    dbm,
                    slug=slug,
                    name=name,
                    primitive_type='number',
                    mdg=mdg,
                    tags=['Education', 'MDG']
                )
                datadict_types[slug] = dd_type.save()
            if row['value'] is not None:
                data = [(slug, row['value'].strip(), get_datadict_type(dbm, datadict_types[slug]))]
            else:
                data = [(slug, row['value'], get_datadict_type(dbm, datadict_types[slug]))]
            if location in locations:
                lga_loaded.append(lga)
                e = dbm.get(locations[location], Entity)
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
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
            slug = str(slugify(unicode(row['indicator'].strip(), 'utf-8')))
            name = row['indicator'].strip()
            lga = row['lga'].strip()
            state = row['state'].strip()
            mdg = row['mdg'].strip()
            location = ("Nigeria", state, lga)
            if not slug in datadict_types:
                dd_type = DataDictType(
                    dbm,
                    slug=slug,
                    name=name,
                    primitive_type='number',
                    mdg=mdg,
                    tags=['Infrastructure', 'MDG']
                )
                datadict_types[slug] = dd_type.save()
            data = [(slug, row['value'].strip(), get_datadict_type(dbm, datadict_types[slug]))]
            if location in locations:
                lga_loaded.append(lga)
                e = dbm.get(locations[location], Entity)
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
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
            slug = str(slugify(unicode(row['indicator'].strip(), 'utf-8')))
            name = row['indicator'].strip()
            lga = row['lga'].strip()
            state = row['state'].strip()
            mdg = row['mdg'].strip()
            location = ("Nigeria", state, lga)
            if not slug in datadict_types:
                dd_type = DataDictType(
                    dbm,
                    slug=slug,
                    name=name,
                    primitive_type='number',
                    mdg=mdg,
                    tags=['Health', 'MDG']
                )
                datadict_types[slug] = dd_type.save()
            data = [(slug, row['value'].strip(), get_datadict_type(dbm, datadict_types[slug]))]
            if location in locations:
                lga_loaded.append(lga)
                e = dbm.get(locations[location], Entity)
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
            else:
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded %d out of %d records" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
        if lga_failed:
            print "%d LGAs failed to load:" % len(lga_failed)
            for lga in lga_failed:
                print "\t%s" % lga
