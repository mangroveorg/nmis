#!/usr/bin/env python
# encoding=utf-8

import os
import sys
import django.core.handlers.wsgi

import os
abs_path = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(abs_path)

sys.path.append(ROOT_DIR)

# Set the django settings and define the wsgi app
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = django.core.handlers.wsgi.WSGIHandler()

# Mount the application to the url
#applications = {'/': 'application',}
