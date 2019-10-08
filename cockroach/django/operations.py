from django.db.backends.postgresql.operations import (
    DatabaseOperations as PostgresDatabaseOperations,
)
from pytz import timezone


class DatabaseOperations(PostgresDatabaseOperations):
    """
    Cockroach currently doesn't allow for deferrable constraints. Feature is
    tracked here: https://github.com/cockroachdb/cockroach/issues/31632
    """
    def deferrable_sql(self):
        return ''

    """
    If a datetime doesn't have a tzinfo then psycopg2 will cast
    the datetime to a TIMESTAMP, which will cause a type error in Cockroach. If
    we specify a tzinfo then psycopg2 will cast it to a TIMESTAMPTZ
    """
    def adapt_datetimefield_value(self, value):
        if value is not None and value.tzinfo is None and self.connection.timezone_name is not None:
            connection_timezone = timezone(self.connection.timezone_name)
            return connection_timezone.localize(value)
        return value

    def sequence_reset_by_name_sql(self, style, sequences):
        # Not implemented by cockroachdb: https://github.com/cockroachdb/cockroach/issues/20956
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
