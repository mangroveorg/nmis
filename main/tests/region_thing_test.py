# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest

from nmis.main.region_thing import RegionThing, import_region_thing_from_dict

class TestRegionThing(unittest.TestCase):
    def setUp(self):
        sample_regions = {
          u'name': u'USA',
          u'slug': u'usa',
          u'children': [
            {
              u'name': u'North West',
              u'slug': u'north_west',
              u'children': [
                {
                  u'children': [
                    {
                      u'name': u'Seattle',
                      u'slug': u'seattle'
                    },
                    {
                      u'name': u'Tacoma',
                      u'slug': u'tacoma'
                    }
                  ],
                  u'name': u'Washington',
                  u'slug': u'wa'
                }
              ]
            },
            {
              u'name': u'North East',
              u'slug': u'north_east',
              u'children': [
                {
                  u'name': u'Massachusetts',
                  u'slug': u'ma',
                  u'children': [
                    {
                      u'name': u'Boston',
                      u'slug': u'boston'
                    },
                    {
                      u'name': u'Worchester',
                      u'slug': u'woostah'
                    }
                  ]
                }
              ]
            },
            {
              u'name': u'South West',
              u'slug': u'south_west',
              u'children': [
                {
                  u'name': u'Arizona',
                  u'slug': u'az',
                  u'children': [
                    {
                      u'name': u'Page',
                      u'slug': u'page'
                    },
                    {
                      u'name': u'Tuscon',
                      u'slug': u'tuscon'
                    }
                  ]
                }
              ]
            },
            {
              u'name': u'South East',
              u'slug': u'south_east',
              u'children': [
                {
                  u'name': u'Florida',
                  u'slug': u'fl',
                  u'children': [
                    {
                      u'name': u'Key West',
                      u'slug': u'key_west'
                    },
                    {
                      u'name': u'Orlando',
                      u'slug': u'orlando'
                    }
                  ]
                }
              ]
            }
          ]
        }
        
        self.usa = import_region_thing_from_dict(sample_regions)
        worchester_slug_array = ['usa', 'north_east', 'ma', 'woostah']
        self.worchester = self.usa.find_child_by_slug_array(worchester_slug_array)
        
        exported_dict = self.usa.export_to_dict()
        self.reimported = import_region_thing_from_dict(exported_dict)
    
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
    
    def test_export_and_import(self):
        #one of the tests from before to test the hierarchy was implemented correctly
        worchester_slug_array = ['usa', 'north_east', 'ma', 'woostah']
        w = self.reimported.find_child_by_slug_array(worchester_slug_array)
        worchester_expected_path = "usa/north_east/ma/woostah"
        self.assertEqual(worchester_expected_path, w.path())
