#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

""" Image file server """

import os
import json

from django.conf import settings
from django.http import (HttpResponse, HttpResponseBadRequest, \
                         HttpResponseRedirect, HttpResponseNotFound)
from django.shortcuts import redirect

MIME_JSON = 'application/json'


def index(request):
    readme = "%s\n -----------------\n\n" % __doc__
    readme += u"\n\n".join(["%s\n%s" % (func[0], func[1].__doc__) \
                            for func in \
                            [('/all', all), \
                             ('info/<pic_id>/', info), \
                             ('/fwd/<pic_id>/<format>/', forward), \
                             ('magic/<pic_id>/<command>/', magic_forward)]])
    return HttpResponse(readme, mimetype='text/plain')


def all(request):
    """ list all images available in JSON """
    data = os.listdir(settings.PICTURES_FOLDER)
    return HttpResponse(json.dumps(data), mimetype=MIME_JSON)


def info(request, pic_id):
    """ list available sizes for image in JSON """
    sizes = _sizes_for_picture(pic_id)
    data = {'id': pic_id, 'sizes': sizes}
    return HttpResponse(json.dumps(data), mimetype=MIME_JSON)


def forward(request, pic_id, format='raw'):
    """ forwards to image file from existing file format """
    pic_folder = os.path.join(settings.PICTURES_FOLDER, pic_id)
    size_folder = os.path.join(pic_folder, format)
    try:
        file_name = os.listdir(size_folder)[0]
    except OSError:
        file_name = 'unknown'
    file_path = os.path.join(os.path.join(pic_id, format), file_name)
    file_url = '%s%s' % (settings.PICTURES_URL, file_path)
    return HttpResponseRedirect(file_url)


def magic_forward(request, pic_id, command='smallest', default_to='raw'):
    """ forwards to image file automaticaly finding appropraite format

 from user defined 'preferences'.
 COMMANDS:
    smallest: Smallest size available
    largest: Largest redimentioned size.
    raw: Original image. Can be big
    hmax=xxx: Size which as height under xxx
    wmax=xxx: Size which width is under xxx
    hmin=xxx: Size with minimum height of xxx
    wmin=xxx: Size with minimum height of xxx
    format=xxx: A known existing format """

    sizes = _sizes_for_picture(pic_id)
    if sizes.__len__() == 0:
        return HttpResponseNotFound("This picture ID does not exist or has " \
                                    "no available format.")
    elif sizes.__len__() == 1:
        format = sizes[0]
    else:
        # guess format here
        format = sizes[0]
    return redirect(forward, pic_id, format)


def _sizes_for_picture(pic_id):
    pic_folder = os.path.join(settings.PICTURES_FOLDER, pic_id)
    try:
        return os.listdir(pic_folder)
    except OSError:
        return []
