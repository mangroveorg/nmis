from django.http import HttpResponse
from django.conf import settings
from mangrove.datastore.database import DatabaseManager
import mangrove.datastore.entity
import json

def by_lga(request):
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE']
    )
    lgas = mangrove.datastore.entity.get_entities_by_type(dbm, 'LGA')
    return HttpResponse("LGAs (%d)<br/>" % len(lgas) + "<br/>\n".join([str(lga.aggregation_paths['_geo']) for lga in lgas]))
