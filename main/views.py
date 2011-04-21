from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from mangrove.datastore.database import DatabaseManager
import mangrove.datastore.entity

def main(request):
    return render_to_response('index.html')

def by_lga(request):
    dbm = DatabaseManager(
        server=settings.MANGROVE_DATABASES['default']['SERVER'],
        database=settings.MANGROVE_DATABASES['default']['DATABASE']
    )
    lgas = mangrove.datastore.entity.get_entities_by_type(dbm, 'LGA')
    lga_data = {}
    for lga in lgas:
        data = lga.get_all_data()
        if len(data):
            lga_data[lga] = data
    return render_to_response('mdgs/lga-data.html', {'lga_data': lga_data})
