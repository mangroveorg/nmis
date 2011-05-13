"""
This is stuff that we will ultimately pull from the data dict, I think.
For now, I'm hard coding it.
--AD

At the end of this file, this command:
 
    INDICATORS = convert_pasted_data()

will generate a list in this format--

[
  {
    "sector": "Education",
    "data_source": "HNLSS",
    "name": "Net enrollment ratio for primary education",
    "lga_display": True,
    "goal_number": 2,
    "country_display": True,
    "subsector": "Enrollment rates"
  }
]
"""

#Spreadsheet located in dropbox:
# Dropbox/NMIS - Nigeria/MDG Indicator List/MDG_consolidated_list_v2.xls
pasted_from_spreadsheet = """
net_enrollment_ratio_for_primary_education_lga	YES	YES	Education	Enrollment rates	2	Net enrollment ratio for primary education  	HNLSS
gross_enrollment_ratio_in_primary_education_lga	YES	YES	Education	Enrollment rates	2	Gross enrollment ratio in primary education  	HNLSS
net_enrollment_ratio_for_secondary_education_lga	NO	YES	Education	Enrollment rates	2	Net enrollment ratio for secondary education	HNLSS
gross_enrollment_ratio_for_secondary_education_lga	NO	YES	Education	Enrollment rates	2	Gross enrollment ratio for secondary education  	HNLSS
transition_rate_from_primary_to_js1_total_lga	YES	YES	Education	Transition rates	2	Transition rate for females from primary to JS1 	School Census 2005
i6	YES	YES	Education	Transition rates	2	Transition rate for males from primary to JS1  	School Census 2005
i7	YES	YES	Education	Repetition rates	2	Percent Male repeaters in primary school 	School Census 2005
i8	YES	YES	Education	Repetition rates	2	Percent Female repeaters in primary school 	School Census 2005
literacy_rate_lga	YES	YES	Education	Literacy rate	2	Literacy rate (Percent) 	HNLSS 
boys_girls_ratio_primary_school_age_lga	YES	YES	Gender	Student Flows	3	Ratio of girls to boys in primary schools  	?
immunization_rate_dpt_3	YES	YES	Health	Child Health	4	Immunization rate (DPT 3) 	DHS 2008
i12	NO	YES	Health	Health Provider	4	Skilled health provider: population ratio 	(facility inventories)
i13	NO	YES	Health	Health Provider	4	Midwife: population ratio 	(facility inventories)
prevalence_of_underweight_weight_for_age_in_children_under_5_years_2sd_from_mean_z_score	YES	YES	Health	Child Health	4	Prevalence of underweight (weight-for-age) in children under 5 years (-3SD from mean Z-score) 	DHS 2008
i15	NO	YES	Health	Health Provider	4	CHW: population ratio 	(facility inventories)
prevalence_of_stunting_height_for_age_in_children_under_5_years_2sd_from_mean_z_score	YES	YES	Health	Child Health	4	Prevalence of stunting (height-for-age) in children under 5 years (-3SD from mean Z-score) 	DHS 2008
prevalence_of_wasting_weight_for_height_in_children_under_5_years_2sd_from_the_mean_z_scores	YES	YES	Health	Child Health	4	Prevalence of wasting (weight-for-height) in children under 5 years (-3SD from the mean Z-scores) 	DHS 2008
under_5_child_mortality_rate	YES	YES	Health	Child Health	4	Under 5 mortality rate 	(DHS 2008)
contraceptive_prevalence_rate_among_married_or_in_union_women_aged_15_49_years_all_methods	YES	YES	Health	Maternal Health	5	Contraceptive prevalence rate among married or in-union women aged 15-49 years  [modern methods]  	DHS 2008 [from table]
proportion_of_births_attended_by_skilled_health_personnel	YES	YES	Health	Maternal Health	5	Proportion of births attended by skilled health personnel 	HNLSS 2009
percentage_of_individuals_that_have_been_tested_for_hiv_ever	YES	YES	Health	HIV & AIDS	6	Percentage of women that have been tested for HIV ever 	DHS 2008
percentage_of_individuals_that_have_been_tested_for_hiv_ever	YES	YES	Health	HIV & AIDS	6	Percentage of men that have been tested for HIV ever 	DHS 2008
percentage_households_with_access_to_improved_water_sources	YES	YES	Infrastructure	Water access	7	Percentage households with access to improved water sources	?
percentage_households_with_access_to_improved_sanitation	YES	YES	Infrastructure	Sanitation access	7	Percentage households with access to improved sanitation	?
"""

def convert_pasted_data():
   lines = pasted_from_spreadsheet.strip().split("\n")
   q = [l.split("\t") for l in lines]
   r = []
   for d in q:
       o = {'slug': d[0],
            'country_display': d[1]=="YES",
           'lga_display': d[2]=="YES",
           'sector': d[3],
           'subsector': d[4],
           'goal_number': int(d[5]),
           'name': d[6].strip(),
           'data_source': d[7].strip()
           }
       r.append(o)
   return r

INDICATORS = convert_pasted_data()