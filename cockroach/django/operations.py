from django.db.backends.postgresql.operations import DatabaseOperations as PostgresDatabaseOperations

from django.utils import timezone


class DatabaseOperations(PostgresDatabaseOperations):
    def deferrable_sql(self):
        return ''
