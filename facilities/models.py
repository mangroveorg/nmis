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
            dd['sector'] = self.SECTOR
            dd['name'] = self.name
            if ll is not None:
                lat, lng, alt, acc = self.latlng_str.split(" ")
                dd['latlng'] = ','.join([lat, lng])
            dd['image_id'] = self.photo_id
            return dd

    class Meta:
        abstract = True


class ClinicInventory(FacilityInventory):
    SECTOR = "health"


class WaterPointInventory(FacilityInventory):
    SECTOR = "water"
    SECTOR = "water"


class LGAInventory(FacilityInventory):
    SECTOR = "lga"


class EducationInventory(FacilityInventory):
    SECTOR = "education"


class AgricultureInventory(FacilityInventory):
    SECTOR = "agriculture"


class Lga(models.Model):
    geoid = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
