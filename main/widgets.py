
#lists of widgets.
#the index is determined by the number of parent entities exist for an entity.
WIDGETS_BY_REGION_LEVEL = [
#country:
    ["country_map", "country_key_indicators", "country_state_nav"],
#state:
    ["regnav_state", "state_map", "state_mdg_performance"],
#lga:
    ["regnav_lga", "lga_map", "lga_mdg_table", "lga_facilities_table"],
]


def widget_includes_by_region_level(rl=0):
    widgets = WIDGETS_BY_REGION_LEVEL[rl]
    include_templates = ["widgets/%s.html" % w for w in widgets]
    return (widgets, include_templates)
