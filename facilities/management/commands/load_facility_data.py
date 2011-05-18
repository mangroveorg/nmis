from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os

from facilities.models import *
import json
import re

FACILITY_CSV_DATA = os.path.join(settings.CURRENT_DIR, 'facilities', 'data')

def remove_quotes(str):
    return re.sub("\"$", "", re.sub("^\"", "", str))

def convert_to_list(csvstr):
    lines = csvstr.strip().split("\n")
    cols = [remove_quotes(l) for l in lines[0].split(",")]
    rows = []
    for row in lines[1:]:
        row_vals = [remove_quotes(r) for r in row.split(",")]
        row_dict = {}
        for i in range(len(cols)):
            row_dict[cols[i]] = row_vals[i]
        rows.append(row_dict)
    return rows

class Command(BaseCommand):
    help = "Loads the facility data to sql."
    def handle(self, *args, **options):
        if len(args)==1 and args[0]=="reload":
            print "Deleting all inventory data"
            for e in EducationInventory.objects.all():
                e.delete()
            for c in ClinicInventory.objects.all():
                c.delete()
        def convert_csv(sector, cls):
            with open(os.path.join(FACILITY_CSV_DATA, "%s.csv" % sector)) as f:
                healths = convert_to_list(f.read())
                for h in healths:
                    photo_id = h.pop('photo')
                    hname = h.pop('name')
                    hgps = h.pop('gps')
                    geoid = h.pop('geo_id', h.pop('geoid', None))
                    hobj, created = cls.objects.get_or_create(photo_id=photo_id)
                    if created:
                        hobj.name = hname
                        hobj.latlng_str = hgps
                        hobj.display_values = json.dumps(h)
                        hobj.lga_geoid = geoid
                        hobj.save()
                print "%s yielded %d Facilities in DB" % (sector, cls.objects.count())
        convert_csv('education', EducationInventory)
        convert_csv('health', ClinicInventory)
