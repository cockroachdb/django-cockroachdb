from django.db.backends.base.base import timezone_constructor
from django.db.backends.postgresql.operations import (
    DatabaseOperations as PostgresDatabaseOperations,
)


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

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        # CockroachDB doesn't support resetting sequences.
        return super().sql_flush(style, tables, reset_sequences=False, allow_cascade=allow_cascade)
