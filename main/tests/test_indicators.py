# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
import datetime
from pytz import UTC
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import Entity
from mangrove.datastore.datadict import DataDictType
from nmis.main.indicators import ScoreDataDictType


class TestScoreDataDictType(unittest.TestCase):

    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        self.create_data_dictionary_entries()
        self.create_entities()
        self.create_data_records()
        self.create_indicators()

    def tearDown(self):
        for e in self.entities:
            # todo: there should be a way to delete entities.
            pass

    def create_data_dictionary_entries(self):
        from nmis.main.health import data_dict_types
        self.data_dict_types = {}
        for kwargs in data_dict_types:
            slug = kwargs['slug']
            data_dict_type = DataDictType(self.dbm, **kwargs)
            self.data_dict_types[slug] = data_dict_type
            self.data_dict_types[slug].save()

    def create_entities(self):
        self.entities = [
            Entity(self.dbm, entity_type="clinic", location=["India"]),
            Entity(self.dbm, entity_type="clinic", location=["India"]),
            ]
        for e in self.entities:
            e.save()

    def create_data_records(self):
        data = [
            {
                "facility_open_247_yn": "yes",
                "all_weather_road_yn": "no",
                "km_to_referral_facility": 15,
                "transport_to_referral_facility_ambulance": 1,
                "inpatient_care_enough_beds_yn": "no",
                },
            ]
        self.february = datetime.datetime(2011, 02, 01, tzinfo=UTC)
        for d, e in zip(data, self.entities):
            for slug, value in d.items():
                data_dict_type = self.data_dict_types[slug]
                e.add_data(
                    data=[(slug, value, data_dict_type)],
                    event_time=self.february
                    )

    def create_indicators(self):
        from nmis.main.health import scores
        self.indicators = {}
        for score in scores:
            slug = score["slug"]
            self.indicators[slug] = ScoreDataDictType(self.dbm, **score)

    def test_access_score_indicator(self):
        access_indicator = self.indicators["access"]
        access_indicator.add_data_records(self.entities[0])
        all_data = self.entities[0].get_all_data()
        self.assertEquals(all_data[self.february][u'access'], 0.5)


class LgaIndicator(unittest.TestCase):

    def setUp(self):
        self.manager = get_db_manager(database='mangrove-test')
        self._create_datadict_types()

    def tearDown(self):
        # _delete_db_and_remove_db_manager(self.manager)
        # should delete data dict types
        pass

    def _create_datadict_types(self):
        self.dd_types = {
            'beds': DataDictType(self.manager, name='beds', slug='beds', primitive_type='number'),
            'meds': DataDictType(self.manager, name='meds', slug='meds', primitive_type='number'),
            'patients': DataDictType(self.manager, name='patients', slug='patients', primitive_type='number'),
            'doctors': DataDictType(self.manager, name='doctors', slug='doctors', primitive_type='number'),
            'director': DataDictType(self.manager, name='director', slug='director', primitive_type='string')
        }
        for label, dd_type in self.dd_types.items():
            dd_type.save()

    def _create_entities_and_data_records(self):
        ENTITY_TYPE = ["Health_Facility", "Clinic"]
        FEB = datetime.datetime(2011, 02, 01, tzinfo=UTC)
        MARCH = datetime.datetime(2011, 03, 01, tzinfo=UTC)

        # Entities for State 1: Maharashtra
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        e.save()

        e.add_data(data=[("beds", 300, self.dd_types['beds']), ("meds", 20, self.dd_types['meds']),
                         ("director", "Dr. A", self.dd_types['director']), ("patients", 10, self.dd_types['patients'])],
                   event_time=FEB)
        e.add_data(data=[("beds", 500, self.dd_types['beds']), ("meds", 20, self.dd_types['meds']),
                         ("patients", 20, self.dd_types['patients'])],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Pune'])
        e.save()
        e.add_data(data=[("beds", 100, self.dd_types['beds']), ("meds", 10, self.dd_types['meds']),
                         ("director", "Dr. AA", self.dd_types['director']), ("patients", 50, self.dd_types['patients'])],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, self.dd_types['beds']), ("meds", 20, self.dd_types['meds']),
                         ("patients", 20, self.dd_types['patients'])],
                   event_time=MARCH)

        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'MH', 'Mumbai'])
        e.save()
        e.add_data(data=[("beds", 100, self.dd_types['beds']), ("meds", 10, self.dd_types['meds']),
                         ("director", "Dr. AAA", self.dd_types['director']), ("patients", 50, self.dd_types['patients'])],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, self.dd_types['beds']), ("meds", 20, self.dd_types['meds']),
                         ("patients", 50, self.dd_types['patients'])],
                   event_time=MARCH)

        # Entities for State 2: karnataka
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Bangalore'])
        e.save()
        e.add_data(data=[("beds", 100, self.dd_types['beds']), ("meds", 250, self.dd_types['meds']),
                         ("director", "Dr. B1", self.dd_types['director']), ("patients", 50, self.dd_types['patients'])],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, self.dd_types['beds']), ("meds", 400, self.dd_types['meds']),
                         ("director", "Dr. B2", self.dd_types['director']), ("patients", 20, self.dd_types['patients'])],
                   event_time=MARCH)
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Karnataka', 'Hubli'])
        e.save()
        e.add_data(data=[("beds", 100, self.dd_types['beds']), ("meds", 250, self.dd_types['meds']),
                         ("director", "Dr. B1", self.dd_types['director']), ("patients", 50, self.dd_types['patients'])],
                   event_time=FEB)
        e.add_data(data=[("beds", 200, self.dd_types['beds']), ("meds", 400, self.dd_types['meds']),
                         ("director", "Dr. B2", self.dd_types['director']), ("patients", 20, self.dd_types['patients'])],
                   event_time=MARCH)
        # Entities for State 3: Kerala
        e = Entity(self.manager, entity_type=ENTITY_TYPE, location=['India', 'Kerala', 'Kochi'])
        e.save()
        e.add_data(data=[("beds", 200, self.dd_types['beds']), ("meds", 50, self.dd_types['meds']),
                         ("director", "Dr. C", self.dd_types['director']), ("patients", 12, self.dd_types['patients'])],
                   event_time=MARCH)

    # def test_lga_indicator(self):
    #     values = 
    #     self.assertEqual(len(values), 3)
    #     self.assertEqual(values[("India", "MH")], {"patients": 200})
    #     self.assertEqual(values[("India", "Karnataka")], {"patients": 140})
    #     self.assertEqual(values[("India", "Kerala")], {"patients": 12})
