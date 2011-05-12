# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
import datetime
from pytz import UTC
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import Entity
from mangrove.datastore.datadict import DataDictType
from nmis.main.indicators import ScoreDataDictType


class TestIndicators(unittest.TestCase):

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
