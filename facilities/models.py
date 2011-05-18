from django.db import models

import json

class FacilityInventory(models.Model):
    name = models.CharField(max_length=50, null=True)
    photo_id = models.CharField(max_length=50, null=True)
    latlng_str = models.CharField(max_length=50, null=True)
    lga_geoid = models.CharField(max_length=50, null=True)
    lga_str = models.CharField(max_length=50, null=True)
    lga_unique_str = models.CharField(max_length=50, null=True)
    data = models.TextField(null=True)
    display_values = models.TextField(null=True)
    
    def display_dict(self):
        if self.display_values is not None:
            dd = json.loads(self.display_values)
            ll = self.latlng_str
            if ll is not None:
                lat, lng, alt, acc = self.latlng_str.split(" ")
                dd['latlng'] = ','.join([lat, lng])
            dd['image_id'] = self.photo_id
            return dd
    
    class Meta:
        abstract = True

class ClinicInventory(FacilityInventory):
    pass

class WaterPointInventory(FacilityInventory):
    pass

class LGAInventory(FacilityInventory):
    pass

class EducationInventory(FacilityInventory):
    pass

class AgricultureInventory(FacilityInventory):
    pass

class Lga(models.Model):
    geoid = models.CharField(max_length=50)
    active = models.BooleanField(default=False)