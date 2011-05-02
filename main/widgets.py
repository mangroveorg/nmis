
#space separated lists of widgets.
#the index is determined by the number of parent entities exist for an entity.
WIDGETS_BY_REGION_LEVEL = [
    "country_view mdg_table",
    "state_view mdg_table",
    "lga_view mdg_table"
]

def widget_includes_by_region_level(rl=0):
    widgets = WIDGETS_BY_REGION_LEVEL[rl].split(" ")
    include_templates = ["widgets/%s.html" % w for w in widgets]
    return (widgets, include_templates)
