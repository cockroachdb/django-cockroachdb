from datetime import timedelta

from django.db.backends.postgresql.operations import (
    DatabaseOperations as PostgresDatabaseOperations,
)
from pytz import timezone


class DatabaseOperations(PostgresDatabaseOperations):
    def deferrable_sql(self):
        # Deferrable constraints aren't supported:
        # https://github.com/cockroachdb/cockroach/issues/31632
        return ''

    def adapt_datetimefield_value(self, value):
        """
        Add a timezone to datetimes so that psycopg2 will cast it to
        TIMESTAMPTZ (as cockroach expects) rather than TIMESTAMP.
        """
        # getattr() guards against F() objects which don't have tzinfo.
        if value and getattr(value, 'tzinfo', '') is None and self.connection.timezone_name is not None:
            connection_timezone = timezone(self.connection.timezone_name)
            try:
                value = connection_timezone.localize(value)
            except OverflowError:
                # Localizing datetime.datetime.max (used to cache a value
                # forever, for example) may overflow. Subtract a day to prevent
                # that.
                value -= timedelta(days=1)
                value = connection_timezone.localize(value)
        return value

    def sequence_reset_by_name_sql(self, style, sequences):
        # Not implemented: https://github.com/cockroachdb/cockroach/issues/20956
        return []

    def sequence_reset_sql(self, style, model_list):
        return []

    def date_extract_sql(self, lookup_type, field_name):
        # Extract SQL is slightly different from PostgreSQL.
        # https://www.cockroachlabs.com/docs/stable/functions-and-operators.html
        if lookup_type == 'week_day':
            # For consistency across backends, return Sunday=1, Saturday=7.
            return 'EXTRACT(dow FROM %s) + 1' % field_name
        elif lookup_type == 'iso_year':
            return 'EXTRACT(isoyear FROM %s)' % field_name
        else:
            return 'EXTRACT(%s FROM %s)' % (lookup_type, field_name)
