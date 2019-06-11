from django.db.backends.postgresql.features import DatabaseFeatures as PostgresDatabaseFeatures


class DatabaseFeatures(PostgresDatabaseFeatures):
    supports_timezones = False
