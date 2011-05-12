# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        from nmis.main.health import HealthScores
        dbm = self._get_database_manager()
        HealthScores.create_health_scores(dbm)
        HealthScores.calculate_health_scores(dbm)

    def _get_database_manager(self):
        from django.conf import settings
        from mangrove.datastore.database import DatabaseManager
        server = settings.MANGROVE_DATABASES['default']['SERVER']
        database = settings.MANGROVE_DATABASES['default']['DATABASE']
        return DatabaseManager(server=server, database=database)
