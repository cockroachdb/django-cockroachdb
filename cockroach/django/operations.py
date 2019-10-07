from django.db.backends.postgresql.operations import DatabaseOperations as PostgresDatabaseOperations
from pytz import timezone
import pytz


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
        return []

    def sequence_reset_sql(self, style, model_list):
        return []
