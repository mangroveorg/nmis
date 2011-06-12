# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import operator
from mangrove.datastore.data import LocationAggregration
from mangrove.datastore.datadict import DataDictType


class ScoreDataDictType(DataDictType):

    def __init__(self, *args, **kwargs):
        self._score_builder = ScoreBuilder()
        components = kwargs.pop("components")
        self._score_builder.add_components(components)
        f = self._score_builder.get_formula()
        self.set_formula(f)
        super(ScoreDataDictType, self).__init__(*args, **kwargs)

    def set_formula(self, f):
        """
        This formula will be applied to each dictionary of data for
        each event time. This dictionary of data looks like:
        {slug : {type, value, label}}
        """
        self._formula = f

    def _calculate_value_by_event_time(self, entity):
        all_data = entity.get_all_data()
        self._value = {}
        for event_time, data in all_data.items():
            self._value[event_time] = self._formula(data)

    def add_data_records(self, entity):
        self._calculate_value_by_event_time(entity)
        for event_time, value in self._value.items():
            entity.add_data(
                data=[(self.slug, value, self)],
                event_time=event_time
                )


class ScoreBuilder(object):
    """
    Helper object for score indicators, build formulas piece by piece
    using this class.
    """

    def __init__(self, *args, **kwargs):
        self.reset()

    def reset(self):
        self._components = []

    def _add_function(self, f):
        self._components.append(f)

    def _add_operator(self, slug, op, value):
        def result(data):
            if slug not in data:
                return None
            return 1 if op(data[slug], value) else 0
        self._components.append(result)

    OPERATORS = {
        "equals": operator.eq,
        "less than": operator.lt,
        }

    def _add_readable_operator(self, slug, op_string, value):
        op = self.OPERATORS[op_string]
        self._add_operator(slug, op, value)

    def add_components(self, components):
        for component in components:
            if type(component) == tuple:
                self._add_readable_operator(*component)
            else:
                self._add_function(component)

    def get_formula(self):
        def formula(data):
            numerator = 0.0
            denominator = 0.0
            for component in self._components:
                value = component(data)
                if value is not None:
                    denominator += 1
                    numerator += value
            if denominator == 0:
                return None
            return numerator / denominator
        return formula


class LgaIndicator(DataDictType):

    from mangrove.datastore import data
    FIELDS = ["entity_type", "data_type_slug", "function_name"]

    def __init__(self, *args, **kwargs):
        for field in self.FIELDS:
            private_field_name = "_" + field
            setattr(self, private_field_name, kwargs.pop(field, None))
        super(LgaIndicator, self).__init__(*args, **kwargs)

    def set_entity_type(self, entity_type):
        self._entity_type = entity_type

    def set_data_type_slug(self, data_type_slug):
        self._data_type_slug = data_type_slug

    def set_function_name(self, function_name):
        assert function_name in self.data.reduce_functions.SUPPORTED_FUNCTIONS
        self._function_name = function_name

    def get_values(self, level):
        # Note: the database manager is inherited from DataDictType
        # which inherits it from DataObject. Is it possible that this
        # type would be stored in one database and the data would be
        # in another!?
        kwargs = {
            "dbm": self._dbm,
            "entity_type": self._entity_type,
            "aggregates": {self._data_type_slug: self._function_name},
            "aggregate_on": LocationAggregration(level=level),
            }
        return self.data.aggregate_by_entity(**kwargs)
