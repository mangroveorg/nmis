def access_to_referral_hospital(data):
    if "km_to_referral_facility" not in data or \
            "transport_to_referral_facility_ambulance" not in data:
        return None
    # todo: make sure 1 is the correct coding for transport to
    # referral facility being available.
    if data.get("km_to_referral_facility") < 10 or \
            data.get("transport_to_referral_facility_ambulance") == 1:
        return 1
    return 0


def physical_condition(data):
    slug = "health_facility_condition"
    if slug not in data:
        return None
    if data.get(slug) == "newly_constructed" or \
            data.get(slug) == "notnew_wellmaintain":
        return 1
    return 0


def convert_to_number(string):
    try:
        f = float(string)
        i = int(string)
        if i == f:
            return i
        return f
    except:
        return 0


def at_least_one_doctor_nurse_or_midwife(data):
    keys = [
        "num_doctors_fulltime",
        "num_midwives_fulltime",
        "num_nurses_fulltime"
        ]
    counts = [convert_to_number(data.get(key)) for key in keys]
    if counts == [0, 0, 0]:
        return 0
    if len([count for count in counts if count >= 1]) > 0:
        return 1
    return None


def at_least_one_chew(data):
    count = convert_to_number(data.get("num_chews_fulltime"))
    if count is None:
        return None
    if count >= 1:
        return 1
    return 0


def at_least_one_technician_if_facility_has_lab(data):
    if data.get("laboratory_yn") == "no":
        return None
    if convert_to_number(data.get("num_lab_techs_fulltime")) >= 1:
        return 1
    return 0


def no_user_fees_for_maternal_health_services(data):
    keys = [
        "paid_services_routine_antenatal_visit",
        "paid_services_contraceptives",
        "paid_services_anc_delivery",
        ]
    fees = [data.get(key) for key in keys]
    if fees == ["FALSE", "FALSE", "FALSE"]:
        return 1
    return 0


class HealthScores(object):

    SCORES = [
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
        {
            "name": 'Staffing',
            "slug": "staffing",
            "primitive_type": 'formula',
            "description": 'Staffing score for health facility.',
            "components": [
                at_least_one_doctor_nurse_or_midwife,
                at_least_one_chew,
                at_least_one_technician_if_facility_has_lab,
                ("staff_quarters_yn", "equals", "yes"),
                ("days_facility_understaffed", "less than", 7),
                ("staff_paid_lastmth_yn", "equals", "yes"),
                ]
            },
        {
            "name": 'Services Provided (Child Health)',
            "slug": "child_services",
            "primitive_type": 'formula',
            "description": 'Services Provided (Child Health)',
            "components": [
                ("child_health_srvcs_bcg_immunization", "equals", "TRUE"),
                ("child_health_srvcs_growth_monitoring", "equals", "TRUE"),
                ("malaria_treatment_yn", "equals", "TRUE"),
                ("child_health_srvcs_dewormig", "equals", "TRUE"),
                ("paid_services_child_health_services", "equals", "FALSE"),
                ]
            },
        {
            "name": 'Services Provided (Maternal Health)',
            "slug": "maternal_services",
            "primitive_type": 'formula',
            "description": 'Services Provided (Maternal Health)',
            "components": [
                ("antenatal_care_yn", "equals", "yes"),
                ("family_planning_yn", "equals", "yes"),
                ("hiv_treatment_srvcs_pmtct_services", "equals", "TRUE"),
                ("emergency_obstetrics_yn",  "equals", "yes"),
                ("emergency_transport_ambulance", "equals", "TRUE"),
                no_user_fees_for_maternal_health_services,
                ]
            },
        {
            "name": 'Services Provided (HIV/TB)',
            "slug": "hiv_services",
            "primitive_type": 'formula',
            "description": 'Services Provided (HIV/TB)',
            "components": [
                ("hiv_treatment_srvcs_counselors", "equals", "FALSE"),
                ("hiv_treatment_srvcs_pmtct_services", "equals", "TRUE"),
                ("hiv_treatment_yn", "equals", "yes"),
                ("lab_tests_performed_tb_microscopy", "equals", "TRUE"),
                ("tb_treatment_yn", "equals", "yes"),
                ]
            },
        {
            "name": 'Equipment / Supplies',
            "slug": "equipment_supplies",
            "primitive_type": 'formula',
            "description": 'Equipment / Supplies',
            "components": [
                ("xray_funct_yn", "equals", "yes"),
                ("ultra_sound_funct_yn", "equals", "yes"),
                ("refrigerator_funct_yn", "equals", "yes"),
                ("emergency_transport_ambulance", "equals", "TRUE",),
                ("equipment_available_operating_surgical_theatre", "equals", "TRUE"),
                ("laboratory_yn", "equals", "yes"),
                # 'No stockouts >1 week in past 3 months',
                ("antimalarials_stockout_yn", "equals", "no"),
                ]
            },
        ]

    @classmethod
    def create_health_scores(cls, dbm):
        from indicators import ScoreDataDictType
        cls._health_scores = {}
        for score in cls.SCORES:
            slug = score["slug"]
            cls._health_scores[slug] = ScoreDataDictType(dbm, **score)

    @classmethod
    def get_health_score(cls, slug):
        return cls._health_scores[slug]

    @classmethod
    def calculate_health_scores(cls, dbm):
        for slug, health_score in cls._health_scores.items():
            print "[started calculating %s]" % slug
            for entity in cls._get_health_facilities(dbm):
                health_score.add_data_records(entity)

    @classmethod
    def _get_health_facilities(cls, dbm):
        from mangrove.datastore.entity import get_entities_by_type
        return get_entities_by_type(dbm, "Health Clinic")
