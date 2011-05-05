
#lists of widgets.
#the index is determined by the number of parent entities exist for an entity.
WIDGETS_BY_REGION_LEVEL = [
#country:
    ["country_view", "mdg_table", "some_metadata"],
#state:
    ["state_view", "mdg_table", "table_ranking", "some_metadata"],
#lga:
    ["lga_view", "mdg_table", "some_metadata"],
]


def widget_includes_by_region_level(rl=0):
    widgets = WIDGETS_BY_REGION_LEVEL[rl]
    include_templates = ["widgets/%s.html" % w for w in widgets]
    return (widgets, include_templates)
