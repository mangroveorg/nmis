# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
import datetime
from pytz import UTC
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import Entity
from mangrove.datastore.datadict import DataDictType
from nmis.main.indicators import data_dict_type_tuples, CalculatedDataDictType, ScoreBuilder

class TestIndicators(unittest.TestCase):

    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        self.create_data_dictionary_entries()
        self.create_entities()
        self.create_data_records()
        self.create_access_indicator()

    def tearDown(self):
        for e in self.entities:
            # todo: there should be a way to delete entities.
            pass

    def create_data_dictionary_entries(self):
        self.data_dict_types = {}
        for data_dict_type_tuple in data_dict_type_tuples:
            kwargs = dict(zip(('name', 'slug', 'primitive_type', 'description'), data_dict_type_tuple))
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
                'open_247': True,
                'all_weather_road': True,
                'sufficient_beds_past_month': True,
                'no_user_fees': False,
                },
            {
                'open_247': False,
                'all_weather_road': False,
                'sufficient_beds_past_month': True,
                'no_user_fees': True,
                },
            ]
        self.february = datetime.datetime(2011, 02, 01, tzinfo=UTC)
        for d, e in zip(data, self.entities):
            for slug, value in d.items():
                data_dict_type = self.data_dict_types[slug]
                e.add_data(
                    data=[(slug, value, data_dict_type),],
                    event_time=self.february
                    )

    def create_access_indicator(self):
        score_builder = ScoreBuilder()
        slugs = [
            'open_247',
            'all_weather_road',
            'sufficient_beds_past_month',
            'no_user_fees',
            ]
        for slug in slugs:
            score_builder.add_true_component(slug)

        self.access_indicator = CalculatedDataDictType(
            dbm=self.dbm,
            name='Access',
            slug='access',
            primitive_type='formula',
            description='Access score for health facility.'
            )
        self.access_indicator.set_formula(score_builder.get_formula())

    def test_access_score_indicator(self):
        self.access_indicator.add_data_records(self.entities[0])
        all_data = self.entities[0].get_all_data()
        self.assertEquals(all_data[self.february][u'access'][u'value'], 0.75)
