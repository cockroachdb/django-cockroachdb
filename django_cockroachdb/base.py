import re
from contextlib import contextmanager

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

try:
    import psycopg2  # noqa
    import psycopg2.extensions  # noqa
    import psycopg2.extras  # noqa
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading psycopg2 module.\n'
        'Did you install psycopg2 or psycopg2-binary?'
    ) from err

from django.db.backends.postgresql.base import (
    DatabaseWrapper as PostgresDatabaseWrapper,
)

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(PostgresDatabaseWrapper):
    vendor = 'cockroachdb'
    display_name = 'CockroachDB'

    # Override some types from the postgresql adapter.
    data_types = dict(
        PostgresDatabaseWrapper.data_types,
        BigAutoField='integer',
        AutoField='integer',
        DateTimeField='timestamptz',
    )
    data_types_suffix = dict(
        PostgresDatabaseWrapper.data_types_suffix,
        BigAutoField='DEFAULT unique_rowid()',
        AutoField='DEFAULT unique_rowid()',
    )

    SchemaEditorClass = DatabaseSchemaEditor
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    client_class = DatabaseClient

    def check_constraints(self, table_names=None):
        """
        Check each table name in `table_names` for rows with invalid foreign
        key references. This method is intended to be used in conjunction with
        `disable_constraint_checking()` and `enable_constraint_checking()`, to
        determine if rows with invalid references were entered while constraint
        checks were off.
        """
        # cockroachdb doesn't support disabling constraint checking
        # (https://github.com/cockroachdb/cockroach/issues/19444) so this
        # method is a no-op.
        pass

    def chunked_cursor(self):
        return self.cursor()

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit

    @contextmanager
    def _nodb_cursor(self):
        # Overidden to avoid inapplicable "Django was unable to create a
        # connection to the 'postgres' database and will use the first
        # PostgreSQL database instead." warning.
        with super(PostgresDatabaseWrapper, self)._nodb_cursor() as cursor:
            yield cursor

    @cached_property
    def cockroachdb_server_info(self):
        # Something like 'CockroachDB CCL v20.1.0-alpha.20191118-1842-g60d40b8
        # (x86_64-unknown-linux-gnu, built 2020/02/03 23:09:23, go1.13.5)'.
        with self.temporary_connection() as cursor:
            cursor.execute('SELECT VERSION()')
            return cursor.fetchone()[0]

    @cached_property
    def cockroachdb_version(self):
        # Match the numerical portion of the version numbers. For example,
        # v20.1.0-alpha.20191118-1842-g60d40b8 returns (20, 1, 0).
        match = re.search(r'v(\d{1,2})\.(\d{1,2})\.(\d{1,2})', self.cockroachdb_server_info)
        if not match:
            raise Exception(
                'Unable to determine CockroachDB version from version '
                'string %r.' % self.cockroachdb_server_info
            )
        return tuple(int(x) for x in match.groups())
