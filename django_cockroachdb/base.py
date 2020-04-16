from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    import psycopg2  # noqa
    import psycopg2.extensions  # noqa
    import psycopg2.extras  # noqa
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading psycopg2 module.\n'
        'Did you install psycopg2 or psycopg2-binary?'
    ) from err

from django.db.backends.postgresql.base import (    # isort:skip
    DatabaseWrapper as PostgresDatabaseWrapper,
)

from .client import DatabaseClient                  # isort:skip
from .creation import DatabaseCreation              # isort:skip
from .features import DatabaseFeatures              # isort:skip
from .introspection import DatabaseIntrospection    # isort:skip
from .operations import DatabaseOperations          # isort:skip
from .schema import DatabaseSchemaEditor            # isort:skip
from .utils import utc_tzinfo_factory               # isort:skip


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

    def create_cursor(self, name=None):
        cursor = super().create_cursor(name=name)
        # cockroachdb needs a differnt tzinfo_factory than PostgreSQL.
        cursor.tzinfo_factory = utc_tzinfo_factory if settings.USE_TZ else None
        return cursor

    def chunked_cursor(self):
        return self.cursor()

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit
