from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

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
        import couchdb
        import datetime
        import string

        from mangrove.datastore.database import DatabaseManager
        from mangrove.datastore.entity import Entity
        from mangrove.datastore.datadict import DataDictType, get_datadict_type
        import mangrove.datastore.entity
        from mangrove.utils import GoogleSpreadsheetsClient
        from mangrove.utils.helpers import slugify
        import datetime
        from pytz import UTC

        print "Loading 'NIMS Data'..."

        print "\tServer: %s" % server
        print "\tDatabase: %s" % database

        dbm = DatabaseManager(server=server, database=database)

        user_spreadsheets = GoogleSpreadsheetsClient(settings.GMAIL_USERNAME, settings.GMAIL_PASSWORD)
        nims_data = user_spreadsheets['NIMS Data']

        countries = {}
        states = {}
        locations = {}

        print "Importing location entities from 'Nigeria LGAs ALL' worksheet"
        for row in nims_data['Nigeria LGAs ALL']:
            country = row['country'].strip()
            state = row['states'].strip()
            lga = row['lga'].strip()
            location = (country, state, lga)
            if country not in countries:
                e = Entity(dbm, entity_type=["Location", "Country"], location=[country])
                locations[(country)] = e.save()
                countries[country] = e.id
            if state not in states:
                e = Entity(dbm, entity_type=["Location", "State"], location=[country, state])
                locations[(country, state)] = e.save()
                states[state] = e.id
            e = Entity(dbm, entity_type=["Location", "LGA"], location=[country, state, lga])
            locations[location] = e.save()

        print "Countries (%d)" % len(countries)
        print "States (%d)" % len(states)
        print "LGAs (%d)" % (len(locations) - len(countries) - len(states))
        print "Total locations (%d)" % len(locations)

        datadict_types = {}

        print "Adding data from 'Population' worksheet"
        lga_loaded = []
        lga_failed = []
        keys = ['childrenunderfive', '_ddv49', 'genderratios', '_chk2m', '_dkvya', '_db1zf', '_cre1l', '_dcgjs', '_d9ney', '_df9om', '_cokwr', '_cn6ca', 'agegroups', '_d415a', '_ciyn3', '_d5fpr', '_cpzh4', '_cx0b9']
        first_row = True
        for row in nims_data['Population']:
            if first_row:
                first_row = False
                continue
            data_row = True
            for key in keys:
                if not key in row:
                    data_row = False
                    break
            if not data_row:
                continue

            lga              = row['_cpzh4'].strip()
            state            = row['_cn6ca'].strip()
            location         = ("Nigeria", state, lga)
            pop_types = [
                    ('population', 'Population'),
                    ('population_ratio_male', 'Population ratio (male)'),
                    ('population_ratio_female', 'Population ratio (female)'),
                    ('population_ratio_under_4', 'Population ratio (under 4)'),
                    ('population_under_5_male', 'Population (males under 5)'),
                    ('population_under_5_female', 'Population (females under 5)')
            ]
            for datadict_type in pop_types:
                dd_type = DataDictType(
                    dbm,
                    slug=datadict_type[0],
                    name=datadict_type[1],
                    primitive_type='number',
                    tags=['Population', 'General']
                )
                datadict_types[datadict_type[0]] = dd_type.save()

            pop              = int(row['_ciyn3'].strip())
            pop_male         = int(row['_cre1l'].strip())
            pop_female       = int(row['_chk2m'].strip())
            pop_ratio_male   = float(pop_male) / float(pop)
            pop_ratio_female = float(pop_female) / float(pop)
            pop_ratio_u4     = float(row['agegroups'].strip())
            pop_u5_male      = int(float(row['childrenunderfive'].strip()))
            pop_u5_female    = int(float(row['_dkvya'].strip()))
            
            if location in locations:
                lga_loaded.append(lga)
                data = [
                    ('population', pop, get_datadict_type(dbm, datadict_types['population'])),
                    ('population_ratio_male', pop_ratio_male, get_datadict_type(dbm, datadict_types['population_ratio_male'])),
                    ('population_ratio_female', pop_ratio_female, get_datadict_type(dbm, datadict_types['population_ratio_female'])),
                    ('population_ratio_under_4', pop_ratio_u4, get_datadict_type(dbm, datadict_types['population_ratio_under_4'])),
                    ('population_under_5_male', pop_u5_male, get_datadict_type(dbm, datadict_types['population_under_5_male'])),
                    ('population_under_5_female', pop_u5_female, get_datadict_type(dbm, datadict_types['population_under_5_female']))
                ]
                e = mangrove.datastore.entity.get(dbm, locations[location])
                e.add_data(data)
            else:
                #print "...no LGA corresponsing to: %s" % lga
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded data for %d out of %d LGAs" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
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
                e = mangrove.datastore.entity.get(dbm, locations[location])
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
            else:
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded data for %d out of %d LGAs" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
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
                e = mangrove.datastore.entity.get(dbm, locations[location])
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
            else:
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded data for %d out of %d LGAs" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
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
                e = mangrove.datastore.entity.get(dbm, locations[location])
                e.add_data(data, event_time=datetime.datetime(2011, 03, 01, tzinfo=UTC))
            else:
                if not lga in lga_failed:
                    lga_failed.append(lga)

        print "Loaded data for %d out of %d LGAs" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
        if lga_failed:
            print "%d LGAs failed to load:" % len(lga_failed)
            for lga in lga_failed:
                print "\t%s" % lga
