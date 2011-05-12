from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext, loader as template_loader
from django.template.defaultfilters import slugify
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import get_entities_by_type, get_entities_in
import json
import os


from main.raw_mdg_indicator_list import INDICATORS as indicator_list

def list_indicators(request):
    context = RequestContext(request)
    context.ilist = indicator_list
    return render_to_response('list.html', context_instance=context)