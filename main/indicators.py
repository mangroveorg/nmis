# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from mangrove.datastore.datadict import DataDictType

class CalculatedDataDictType(DataDictType):

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

    def add_component(self, numerator, denominator):
        component = {
            'numerator': numerator,
            'denominator': denominator,
            }
        self._components.append(component)

    def get_formula(self):
        def formula(data):
            numerator = 0.0
            denominator = 0.0
            for component in self._components:
                numerator += component['numerator'](data)
                denominator += component['denominator'](data)
            return numerator / denominator
        return formula

    def add_equals_component(self, slug, value):
        def denominator(data):
            return 1 if slug in data else 0
        def numerator(data):
            if slug not in data: return 0
            return 1 if data[slug][u'value']==value else 0
        self.add_component(numerator, denominator)

    def add_true_component(self, slug):
        self.add_equals_component(slug, True)

# name, slug, primitive type, description
data_dict_type_tuples = [
    ('open 24/7', 'open_247', 'boolean', 'Open twenty-four hours a day, seven days a week',),
    ('All weather road', 'all_weather_road', 'boolean', 'All weather road access to the facility.',),
    ('Sufficient beds in past month', 'sufficient_beds_past_month', 'boolean', '',),
    ('No user fees', 'no_user_fees', 'boolean', '',),
    ]

scores = {
    ('Access', 'access', 'formula', 'Access score for health facility.'): [
        'open_247',
        'all_weather_road',
        'sufficient_beds_past_month',
        'no_user_fees',
        ],
    'Infrastructure': [
        'Power',
        'Not without power >1 wk in past month',
        'Potable water',
        'Not without  water >1 wk in past month',
        'Sanitation',
        'Not without sanitation >1 wk in past month',
        'condition of physical structure',
        ],
    'Staffing': [
        '>1 Doctor/nurse/midwife',
        '>1 CHEW',
        'Lab technician (for facililties with labs)',
        'Living quarters',
        'Not understaffed >1 wk in past month',
        'Staff paid in past month',
        ],
    'Services Provided (Child Health)': [
        'Immunization',
        'Growth monitoring',
        'Malaria treatment',
        'Deworming',
        'No user fees for child health services',
        ],
    'Services Provided (Maternal Health)': [
        'Antenatal care',
        'Family planning',
        'PMTCT program',
        'Comprehensive emergency obstetric care',
        'Ambulance',
        'No user fees for maternal health services',
        ],
    'Services Provided (HIV/TB)': [
        'VCT, PMTCT, HIV treatment, TB treatment',
        'VCT',
        'PMTCT',
        'HIV TREATMENT',
        'TB testing',
        'TB treatment',
        ],
    'Equipment / Supplies': [
        'Xray machine',
        'Ultrasound',
        'Refrigerator',
        'Ambulance',
        'Operating theatre',
        'Laboratory',
        'No stockouts >1 week in past 3 months',
        ],
    }

