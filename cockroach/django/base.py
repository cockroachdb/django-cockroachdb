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

    # Override some types from the postgresql adapter.
    data_types = dict(
        PostgresDatabaseWrapper.data_types,
        AutoField='integer',
        DateTimeField='timestamptz',
    )
    data_types_suffix = dict(
        PostgresDatabaseWrapper.data_types_suffix,
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
