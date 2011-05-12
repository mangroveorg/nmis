data_dict_types = [
    {
        "name": 'open 24/7',
        "slug": "facility_open_247_yn",
        "primitive_type": "string",
        "description": 'Open twenty-four hours a day, seven days a week',
        },
    {
        "name": 'All weather road',
        "slug": "all_weather_road_yn",
        "primitive_type": "string",
        "description": 'All weather road access to the facility.',
        },
    {
        "name": 'Distance to referral facility (km).',
        "slug": "km_to_referral_facility",
        "primitive_type": "decimal",
        "description": 'Distance to referral facility (km).',
        },
    {
        "name": "Ambulance transport availabel to referral facility.",
        "slug": "transport_to_referral_facility_ambulance",
        "primitive_type": "string",
        "description": "Ambulance transport availabel to referral facility.",
        },
    {
        "name": 'Sufficient beds',
        "slug": "inpatient_care_enough_beds_yn",
        "primitive_type": "integer",
        "description": "Sufficient beds for inpatient care.",
        },
    ]


# slug of data dict type, and value looking for
def access_to_referral_hospital(data):
    if "km_to_referral_facility" not in data or \
            "transport_to_referral_facility_ambulance" not in data:
        return None
    # todo: make sure 1 is the correct coding for transport to
    # referral facility being available.
    if data["km_to_referral_facility"] < 10 or \
            data["transport_to_referral_facility_ambulance"] == 1:
        return 1
    return 0


def physical_condition(data):
    slug = "health_facility_condition"
    if slug not in data:
        return None
    if data[slug] == "newly_constructed" or \
            data[slug] == "notnew_wellmaintain":
        return 1
    return 0

scores = [
    {
        "name": 'Access',
        "slug": 'access',
        "primitive_type": 'formula',
        "description": 'Access score for health facility.',
        "components": [
            ("facility_open_247_yn", "equals", "yes"),
            ("all_weather_road_yn", "equals", "yes"),
            access_to_referral_hospital,
            ("inpatient_care_enough_beds_yn", "equals", "yes"),
            # I can't find a variable for "No user fees"
            ]
        },
    {
        "name": 'Infrastructure',
        "slug": "infrastructure",
        "primitive_type": 'formula',
        "description": 'Infrastructure score for health facility.',
        "components": [
            ("power_sources_none", "equals", 0),
            ("days_no_electricity", "less than", 7),
            ("days_no_potable_water_pastmth", "less than", 28),
            ("days_no_water_pastmth", "less than", 7),
            ("toilet_types_none", "equals", 0),
            # Not without sanitation >1 wk in past month
            # I'm ignoring this component because we only have days
            # last month not working for each type of toilet, not
            # sanitation in general.
            physical_condition,
            ]
        },
    ]


    # 'Staffing': [
    #     '>1 Doctor/nurse/midwife',
    #     '>1 CHEW',
    #     'Lab technician (for facililties with labs)',
    #     'Living quarters',
    #     'Not understaffed >1 wk in past month',
    #     'Staff paid in past month',
    #     ],
    # 'Services Provided (Child Health)': [
    #     'Immunization',
    #     'Growth monitoring',
    #     'Malaria treatment',
    #     'Deworming',
    #     'No user fees for child health services',
    #     ],
    # 'Services Provided (Maternal Health)': [
    #     'Antenatal care',
    #     'Family planning',
    #     'PMTCT program',
    #     'Comprehensive emergency obstetric care',
    #     'Ambulance',
    #     'No user fees for maternal health services',
    #     ],
    # 'Services Provided (HIV/TB)': [
    #     'VCT, PMTCT, HIV treatment, TB treatment',
    #     'VCT',
    #     'PMTCT',
    #     'HIV TREATMENT',
    #     'TB testing',
    #     'TB treatment',
    #     ],
    # 'Equipment / Supplies': [
    #     'Xray machine',
    #     'Ultrasound',
    #     'Refrigerator',
    #     'Ambulance',
    #     'Operating theatre',
    #     'Laboratory',
    #     'No stockouts >1 week in past 3 months',
    #     ],
    # }
