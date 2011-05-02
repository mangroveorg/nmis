
WIDGETS_BY_REGION_LEVEL = [
    "country_view mdg_table",
    "state_view mdg_table",
    "lga_view mdg_table"
]

def widget_includes_by_region_level(rl=0):
    widgets = WIDGETS_BY_REGION_LEVEL[rl].split(" ")
    return ["widgets/%s.html" % w for w in widgets]
