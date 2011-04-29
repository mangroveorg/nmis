LISTS = [
      {"id": "education_mdg_data",
        "display_method": "mdg_stuff",
        "name": "Education MDG Data"},
      {"id": "infrastructure_mdg_data",
        "display_method": "mdg_stuff",
        "name": "Infrastructure MDG Data"},
      {"id": "health_mdg_data",
        "display_method": "mdg_stuff",
        "name": "Health MDG Data"}
    ]

def get_spreadsheet(ssid):
    for s in LISTS:
        if s['id']==ssid: return s
    return None

SAMPLE_MDG =     {
      "years": [
        2010,
        2009
      ],
      "variables": {
        "1": {
          "name": "Number of Mice caught by Falcons",
          "data_type": "integer",
          "display_order": 2,
          "values": {
            "2010": 5,
            "2009": 15
          },
          "subgoal": "1.1",
          "subgroup": "Male Mice",
          "goal": "1"
        },
        "3": {
          "name": "Number of Mice caught by Falcons",
          "data_type": "integer",
          "display_order": 3,
          "values": {
            "2010": 9,
            "2009": 35
          },
          "subgoal": "1.1",
          "subgroup": "Total",
          "goal": "1"
        },
        "2": {
          "name": "Number of Mice caught by Falcons",
          "data_type": "integer",
          "display_order": 1,
          "values": {
            "2010": 4,
            "2009": 20
          },
          "subgoal": "1.1",
          "subgroup": "Female Mice",
          "goal": "1"
        },
        "5": {
          "name": "Average weight of Falcon",
          "data_type": "decimal",
          "display_order": 2430,
          "values": {
            "2010": 12.33,
            "2009": 20.94
          },
          "subgoal": None,
          "subgroup": None,
          "goal": "6"
        },
        "4": {
          "name": "Professional Falconers",
          "data_type": "integer",
          "display_order": 2540,
          "values": {
            "2010": 10,
            "2009": 4
          },
          "subgoal": "2.3",
          "goal": "2"
        }
      }
    }

import copy
def for_display(sheet_name):
    ss = get_spreadsheet(sheet_name)
    dd = copy.copy(ss)
    dd[u'title'] = "Data from Google Docs: %s" % ss[u'name']
    dd[u'mdg_data'] = SAMPLE_MDG
    display_method = dd.get(u'display_method')
    return (display_method, dd)