#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Generates most Mangrove views to save some time later"
    args = "<server> <database> | <database>"

    def handle(self, *args, **options):
        server = settings.MANGROVE_DATABASES['default']['SERVER']
        database = settings.MANGROVE_DATABASES['default']['DATABASE']
        if len(args) == 2:
            server = args[0]
            database = args[1]
        elif len(args) == 1:
            database = args[0]
        elif len(args) == 0:
            pass
        else:
            raise CommandError('Wrong number of arguments. Run ' \
                               '\'python manage.py help genviews\' for usage.')
        self._generate_views(server, database)

    def _generate_views(self, server, database):

        from mangrove.datastore.database import DatabaseManager
        from mangrove.datastore.views import view_js

        print("Generating Views...")

        print("\tServer: %s" % server)
        print("\tDatabase: %s\n" % database)

        dbm = DatabaseManager(server=server, database=database)

        for view in view_js:
            start = datetime.now()
            print("Generating view `%s`" % view)
            dbm.load_all_rows_in_view('mangrove_views/%s' % view)
            end = datetime.now()
            print("\ttook %d seconds" % (end - start).seconds)
