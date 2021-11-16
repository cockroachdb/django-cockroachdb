import time

from django.db.backends.base.base import timezone_constructor
from django.db.backends.postgresql.operations import (
    DatabaseOperations as PostgresDatabaseOperations,
)
from django.db.utils import OperationalError
from psycopg2 import errorcodes


class DatabaseOperations(PostgresDatabaseOperations):
    integer_field_ranges = {
        'SmallIntegerField': (-32768, 32767),
        'IntegerField': (-9223372036854775808, 9223372036854775807),
        'BigIntegerField': (-9223372036854775808, 9223372036854775807),
        'PositiveSmallIntegerField': (0, 32767),
        'PositiveBigIntegerField': (0, 9223372036854775807),
        'PositiveIntegerField': (0, 9223372036854775807),
        'SmallAutoField': (-32768, 32767),
        'AutoField': (-9223372036854775808, 9223372036854775807),
        'BigAutoField': (-9223372036854775808, 9223372036854775807),
    }
    explain_options = frozenset(['DISTSQL', 'OPT', 'TYPES', 'VEC', 'VERBOSE'])

    def datetime_extract_sql(self, lookup_type, sql, params, tzname):
        if self.connection.features.is_cockroachdb_22_1:
            return super().datetime_extract_sql(lookup_type, sql, params, tzname)
        # Override the changes from https://github.com/django/django/commit/b7f263551c64e3f80544892e314ed5b0b22cc7c8
        # which aren't compatible with older versions of CockroachDB:
        # https://github.com/cockroachdb/cockroach/issues/76960
        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        return self.date_extract_sql(lookup_type, sql, params)

    def time_extract_sql(self, lookup_type, sql, params):
        if self.connection.features.is_cockroachdb_22_1:
            return super().time_extract_sql(lookup_type, sql, params)
        # Override the changes from https://github.com/django/django/commit/b7f263551c64e3f80544892e314ed5b0b22cc7c8
        # which aren't compatible with older versions of CockroachDB:
        # https://github.com/cockroachdb/cockroach/issues/76960
        return self.date_extract_sql(lookup_type, sql, params)

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
            connection_timezone = timezone_constructor(self.connection.timezone_name)
            value = value.replace(tzinfo=connection_timezone)
        return value

    def sequence_reset_by_name_sql(self, style, sequences):
        # Not implemented: https://github.com/cockroachdb/cockroach/issues/20956
        return []

    def sequence_reset_sql(self, style, model_list):
        return []

    def explain_query_prefix(self, format=None, **options):
        extra = []
        # Normalize options.
        if options:
            options = {
                name.upper(): value
                for name, value in options.items()
            }
            for valid_option in self.explain_options:
                value = options.pop(valid_option, None)
                if value:
                    extra.append(valid_option)
        prefix = super().explain_query_prefix(format, **options)
        if extra:
            prefix += ' (%s)' % ', '.join(extra)
        return prefix

    def execute_sql_flush(self, sql_list):
        # Retry TRUNCATE if it fails with a serialization error.
        num_retries = 10
        initial_retry_delay = 0.5  # The initial retry delay, in seconds.
        backoff_ = 1.5  # For each retry, the last delay is multiplied by this.
        next_retry_delay = initial_retry_delay
        for retry in range(1, num_retries + 1):
            try:
                return super().execute_sql_flush(sql_list)
            except OperationalError as exc:
                if (getattr(exc.__cause__, 'pgcode', '') != errorcodes.SERIALIZATION_FAILURE or
                        retry >= num_retries):
                    raise
                time.sleep(next_retry_delay)
                next_retry_delay *= backoff_

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        # CockroachDB doesn't support resetting sequences.
        return super().sql_flush(style, tables, reset_sequences=False, allow_cascade=allow_cascade)
