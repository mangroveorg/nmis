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
YES	YES	Education	Enrollment rates	2	Net enrollment ratio for primary education  	HNLSS
YES	YES	Education	Enrollment rates	2	Gross enrollment ratio in primary education  	HNLSS
NO	YES	Education	Enrollment rates	2	Net enrollment ratio for secondary education	HNLSS
NO	YES	Education	Enrollment rates	2	Gross enrollment ratio for secondary education  	HNLSS
YES	YES	Education	Transition rates	2	Transition rate for females from primary to JS1 	School Census 2005
YES	YES	Education	Transition rates	2	Transition rate for males from primary to JS1  	School Census 2005
YES	YES	Education	Repetition rates	2	Percent Male repeaters in primary school 	School Census 2005
YES	YES	Education	Repetition rates	2	Percent Female repeaters in primary school 	School Census 2005
YES	YES	Education	Literacy rate	2	Literacy rate (Percent) 	HNLSS 
YES	YES	Gender	Student Flows	3	Ratio of girls to boys in primary schools  	?
YES	YES	Health	Child Health	4	Immunization rate (DPT 3) 	DHS 2008
NO	YES	Health	Health Provider	4	Skilled health provider: population ratio 	(facility inventories)
NO	YES	Health	Health Provider	4	Midwife: population ratio 	(facility inventories)
YES	YES	Health	Child Health	4	Prevalence of underweight (weight-for-age) in children under 5 years (-3SD from mean Z-score) 	DHS 2008
NO	YES	Health	Health Provider	4	CHW: population ratio 	(facility inventories)
YES	YES	Health	Child Health	4	Prevalence of stunting (height-for-age) in children under 5 years (-3SD from mean Z-score) 	DHS 2008
YES	YES	Health	Child Health	4	Prevalence of wasting (weight-for-height) in children under 5 years (-3SD from the mean Z-scores) 	DHS 2008
YES	YES	Health	Child Health	4	Under 5 mortality rate 	(DHS 2008)
YES	YES	Health	Maternal Health	5	Contraceptive prevalence rate among married or in-union women aged 15-49 years  [modern methods]  	DHS 2008 [from table]
YES	YES	Health	Maternal Health	5	Proportion of births attended by skilled health personnel 	HNLSS 2009
YES	YES	Health	HIV & AIDS	6	Percentage of women that have been tested for HIV ever 	DHS 2008
YES	YES	Health	HIV & AIDS	6	Percentage of men that have been tested for HIV ever 	DHS 2008
YES	YES	Infrastructure	Water access	7	Percentage households with access to improved water sources	?
YES	YES	Infrastructure	Sanitation access	7	Percentage households with access to improved sanitation	?
"""

def convert_pasted_data():
   lines = pasted_from_spreadsheet.strip().split("\n")
   q = [l.split("\t") for l in lines]
   r = []
   for d in q:
       o = {'country_display': d[0]=="YES",
           'lga_display': d[1]=="YES",
           'sector': d[2],
           'subsector': d[3],
           'goal_number': int(d[4]),
           'name': d[5].strip(),
           'data_source': d[6].strip()
           }
       r.append(o)
   return r

INDICATORS = convert_pasted_data()