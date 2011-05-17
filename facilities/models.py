from django.db import models

class FacilityInventory(models.Model):
    name = models.CharField(max_length=50)
    image_id = models.CharField(max_length=50)
    latlng_str = models.CharField(max_length=50)
    lga_str = models.CharField(max_length=50)
    lga_unique_str = models.CharField(max_length=50)
    data = models.TextField(null=True)
    display_values = models.TextField(null=True)
    
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
