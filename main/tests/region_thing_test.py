# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest

from nmis.main.region_thing import RegionThing

class TestRegionThing(unittest.TestCase):
    def setUp(self):
        self.usa = RegionThing(name="USA", slug="usa")

        nw = RegionThing(name="North West", slug="north_west")
        nw_state = RegionThing(name="Washington", slug="wa")
        wa1 = RegionThing(name="Seattle", slug="seattle")
        wa2 = RegionThing(name="Tacoma", slug="tacoma")
        nw_state._set_subregions([wa1, wa2])
        nw._set_subregions([nw_state])

        ne = RegionThing(name="North East", slug="north_east")
        ne_state = RegionThing(name="Massachusetts", slug="ma")
        ma1 = RegionThing(name="Boston", slug="boston")
        ma2 = RegionThing(name="Worchester", slug="woostah")
        ne_state._set_subregions([ma1, ma2])
        ne._set_subregions([ne_state])
        
        self.worchester = ma2

        sw = RegionThing(name="South West", slug="south_west")
        sw_state = RegionThing(name="Arizona", slug="az")
        az1 = RegionThing(name="Page", slug="page")
        az2 = RegionThing(name="Tuscon", slug="tuscon")
        sw_state._set_subregions([az1, az2])
        sw._set_subregions([sw_state])

        se = RegionThing(name="South East", slug="south_east")
        se_state = RegionThing(name="Florida", slug="fl")
        fl1 = RegionThing(name="Key West", slug="key_west")
        fl2 = RegionThing(name="Orlando", slug="orlando")
        se_state._set_subregions([fl1, fl2])
        se._set_subregions([se_state])

        self.usa._set_subregions([nw, ne, sw, se])
    
    def test_dict_output_of_context_dict(self):
        expected_dict = {
          "name": "USA",
          "level": 0,
          "slug": "usa",
          "parents": [],
          "path": "usa",
          "children": [
            {
              "path": "usa/north_west",
              "children": [
                {
                  "path": "usa/north_west/wa",
                  "name": "Washington",
                  "slug": "wa"
                }
              ],
              "name": "North West",
              "slug": "north_west"
            },
            {
              "path": "usa/north_east",
              "children": [
                {
                  "path": "usa/north_east/ma",
                  "name": "Massachusetts",
                  "slug": "ma"
                }
              ],
              "name": "North East",
              "slug": "north_east"
            },
            {
              "path": "usa/south_west",
              "children": [
                {
                  "path": "usa/south_west/az",
                  "name": "Arizona",
                  "slug": "az"
                }
              ],
              "name": "South West",
              "slug": "south_west"
            },
            {
              "path": "usa/south_east",
              "children": [
                {
                  "path": "usa/south_east/fl",
                  "name": "Florida",
                  "slug": "fl"
                }
              ],
              "name": "South East",
              "slug": "south_east"
            }
          ]
        }
        self.assertEqual(self.usa.context_dict(2),expected_dict)
    
    def test_search_by_slug_array(self):
        worchester_slug_array = ['usa', 'north_east', 'ma', 'woostah']
        w = self.usa.find_child_by_slug_array(worchester_slug_array)
        self.assertEqual(w.name, "Worchester")
    
    def test_usa_info_dict(self):
        expected_info = {'name': 'USA', 'slug': 'usa', 'path': 'usa'}
        self.assertEqual(self.usa.info_dict(), expected_info)
    
    def test_path_is_built(self):
        worchester_expected_path = "usa/north_east/ma/woostah"
        self.assertEqual(worchester_expected_path, self.worchester.path())