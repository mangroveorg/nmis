LISTS = [
      {"id": "education_mdg_data",
        "name": "Education MDG Data"},
      {"id": "infrastructure_mdg_data",
        "name": "Infrastructure MDG Data"},
      {"id": "health_mdg_data",
        "name": "Health MDG Data"}
    ]

def get_spreadsheet(ssid):
    for s in LISTS:
        if s['id']==ssid: return s
    return None

SAMPLE_MDG = {"years": [2010,2009],"variables": {"1": {"name": \
    "Number of Mice caught by Falcons","data_type": "integer", \
    "display_order": 2,"values": {"2010": 5,"2009": 15},"subgoal": \
    "1.1","subgroup": "Male Mice","goal": "1"},"3": {"name": \
    "Number of Mice caught by Falcons","data_type": "integer","display_order": \
    3,"values": {"2010": 9,"2009": 35},"subgoal": "1.1","subgroup": "Total", \
    "goal": "1"},"2": {"name": "Number of Mice caught by Falcons","data_type": \
    "integer","display_order": 1,"values": {"2010": 4,"2009": 20},"subgoal": "1.1", \
    "subgroup": "Female Mice","goal": "1"},"5": {"name": "Average weight of Falcon", \
    "data_type": "decimal","display_order": 2430,"values": {"2010": 12.33,"2009": 20.94}, \
    "subgoal": None,"subgroup": None,"goal": "6"},"4": {"name": "Professional Falconers", \
    "data_type": "integer","display_order": 2540,"values": {"2010": 10,"2009": 4}, \
    "subgoal": "2.3","goal": "2"}}}

import copy
def for_display(sheet_name):
    ss = get_spreadsheet(sheet_name)
    dd = copy.copy(ss)
    dd = {u'id': sheet_name, u'name': ss['name'], \
            u'title': "Data from Google Docs: %s" % ss[u'name'], \
            u'widgets': []}
    
    #display_method matches up to one of the json renderers in jsonRenderer.jquery.js
    mdg_section = {u'display_method': u'mdg_data', u'mdg_data': SAMPLE_MDG}
    dd[u'widgets'].append(mdg_section)
    
    #display_method matches up to one of the json renderers in jsonRenderer.jquery.js
    mdg_section2 = {u'display_method': u'test_json_renderer', u'test': u'something', u'sheet_name': sheet_name}
    dd[u'widgets'].append(mdg_section2)
    return dd