# script to load the NIMS data for locations

import csv
import uuid
import couchdb
import datetime
import string

from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
import mangrove.datastore.entity
from mangrove.utils import GoogleSpreadsheetsClient
from localsettings import GMAIL_USERNAME, GMAIL_PASSWORD

# TODO move this function
import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t :;!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'_'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

print "Loading 'NIMS Data'..."

#reader = csv.reader(open('data/nims_data_loc.csv', 'r'))

dbm = DatabaseManager(server='http://localhost:5984', database='nmis')

user_spreadsheets = GoogleSpreadsheetsClient(GMAIL_USERNAME, GMAIL_PASSWORD)
nims_data = user_spreadsheets['NIMS Data']

countries = {}
states = {}
lgas = {}

print "Importing location entities from 'Nigeria LGAs ALL' worksheet"
for row in nims_data['Nigeria LGAs ALL']:
    country = row['isoctry']
    state   = row['states']
    lga     = row['lga']
    if country not in countries:
        #print "...adding [%s]" % country
        e = Entity(dbm, entity_type=["Location", "Country"], location=[country])
        countries[country] = e.save()
    if state not in states:
        #print "...adding [%s, %s]" % (country, state)
        e = Entity(dbm, entity_type=["Location", "State"], location=[country, state])
        states[state] = e.save()
    if lga not in lgas:
        #print "...adding [%s, %s, %s]" % (country, state, lga)
        e = Entity(dbm, entity_type=["Location", "LGA"], location=[country, state, lga])
        lgas[lga] = e.save()

print "Loaded countries (%d)" % len(countries)
print "Loaded states (%d)" % len(states)
print "Loaded lgas (%d)" % len(lgas)

print "Adding data from 'Population' worksheet"
lga_loaded = []
lga_failed = []
keys = {'childrenunderfive', '_ddv49', 'genderratios', '_chk2m', '_dkvya', '_db1zf', '_cre1l', '_dcgjs', '_d9ney', '_df9om', '_cokwr', '_cn6ca', 'agegroups', '_d415a', '_ciyn3', '_d5fpr', '_cpzh4', '_cx0b9'}
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
    lga              = row['_cpzh4']
    pop              = int(row['_ciyn3'])
    pop_male         = int(row['_cre1l'])
    pop_female       = int(row['_chk2m'])
    pop_ratio_male   = float(pop_male) / float(pop)
    pop_ratio_female = float(pop_female) / float(pop)
    pop_ratio_u4     = float(row['agegroups'])
    pop_u5_male      = int(float(row['childrenunderfive']))
    pop_u5_female    = int(float(row['_dkvya']))
    if lga in lgas:
        lga_loaded.append(lga)
        data = [
            ('population', pop),
            ('population_ratio_male', pop_ratio_male),
            ('population_ratio_female', pop_ratio_female),
            ('population_ratio_under_4', pop_ratio_u4),
            ('population_under_5_male', pop_u5_male),
            ('population_under_5_female', pop_u5_female)
        ]
        e = mangrove.datastore.entity.get(dbm, lgas[lga])
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
indicators = {}

print "Adding data from 'Education MDG Data' worksheet"
lga_loaded = []
lga_failed = []
for row in nims_data['Education MDG Data']:
    slug = str(slugify(unicode(row['indicator'], 'utf-8')))
    data_type = 'numeric'
    lga = row['lga']
    #if not slug in indicators:
    #    indicator = {
    #        'slug': slug,
    #        'name': row['indicator'],
    #        'description': row['indicatordefinition'],
    #        'type': data_type,
    #        'tags': ['Education']
    #    }
    #    indicators[slug] = indicator
    data = [(slug , row['value'])]
    if lga in lgas:
        lga_loaded.append(lga)
        e = mangrove.datastore.entity.get(dbm, lgas[lga])
        e.add_data(data)
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
    slug = str(slugify(unicode(row['indicator'], 'utf-8')))
    data_type = 'numeric'
    lga = row['lga']
    #if not slug in indicators:
    #    indicator = {
    #        'slug': slug,
    #        'name': row['indicator'],
    #        'description': row['indicatordefinition'],
    #        'type': data_type,
    #        'tags': ['Infrastructure']
    #    }
    #    indicators[slug] = indicator
    data = [(slug , row['value'])]
    if lga in lgas:
        lga_loaded.append(lga)
        e = mangrove.datastore.entity.get(dbm, lgas[lga])
        e.add_data(data)
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
    slug = str(slugify(unicode(row['indicator'], 'utf-8')))
    data_type = 'numeric'
    lga = row['lga']
    #if not slug in indicators:
    #    indicator = {
    #        'slug': slug,
    #        'name': row['indicator'],
    #        'description': row['indicatordefinition'],
    #        'type': data_type,
    #        'tags': ['Infrastructure']
    #    }
    #    indicators[slug] = indicator
    data = [(slug , row['value'])]
    if lga in lgas:
        lga_loaded.append(lga)
        e = mangrove.datastore.entity.get(dbm, lgas[lga])
        e.add_data(data)
    else:
        if not lga in lga_failed:
            lga_failed.append(lga)

print "Loaded data for %d out of %d LGAs" % (len(lga_loaded), len(lga_failed) + len(lga_loaded))
if lga_failed:
    print "%d LGAs failed to load:" % len(lga_failed)
    for lga in lga_failed:
        print "\t%s" % lga

