from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

import os
TILE_CACHE_DIR = os.path.join(settings.CURRENT_DIR, "tiles", "tile_cache")

TILE_ROOT_URL = "http://tilestream.openmangrove.org:8888"

import urllib


def tile_cache(request, tile_path):
    return HttpResponseRedirect("/".join([TILE_ROOT_URL, tile_path]))
    #workin progress not done yet.
    if not os.path.exists(TILE_CACHE_DIR):
        os.mkdir(TILE_CACHE_DIR)
    req_tile_file = os.path.join(TILE_CACHE_DIR, tile_path)
    tile_dir_name = os.path.dirname(req_tile_file)
    r = HttpResponse(mimetype="image/png")
    if not os.path.exists(tile_dir_name):
        os.makedirs(tile_dir_name)
    if not os.path.exists(req_tile_file):
        tile_url = "/".join([TILE_ROOT_URL, tile_path])
        try:
            filename, headers = urllib.urlretrieve(tile_url, req_tile_file)
        except:
            with open(os.path.join(TILE_CACHE_DIR, '34.png')) as f:
                r.write(f.read())
                return r
    with open(req_tile_file) as f:
        r.write(f.read())
    return r
